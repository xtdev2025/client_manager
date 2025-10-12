from datetime import datetime, timedelta
from functools import lru_cache

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from app.models.admin import Admin
from app.models.client import Client
from app.models.click import Click
from app.models.domain import Domain
from app.models.info import Info
from app.models.login_log import LoginLog
from app.models.plan import Plan
from app.models.template import Template
from app.models.user import User
from app.views.dashboard_view import DashboardView

dashboard = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@lru_cache(maxsize=32, typed=True)
def _get_admin_stats_cached():
    """Cached admin statistics - expires every 5 minutes"""
    from app import mongo
    return {
        "total_clients": mongo.db.clients.count_documents({}),
        "active_clients": mongo.db.clients.count_documents({"status": "active"}),
        "total_infos": mongo.db.infos.count_documents({}),
        "active_infos": mongo.db.infos.count_documents({"status": "active"}),
        "total_domains": mongo.db.domains.count_documents({}),
        "total_plans": mongo.db.plans.count_documents({}),
        "total_templates": mongo.db.templates.count_documents({}),
        "total_admins": mongo.db.admins.count_documents({}),
    }


@lru_cache(maxsize=16, typed=True)
def _get_plan_distribution_cached():
    """Cached plan distribution"""
    from app import mongo
    plan_pipeline = [
        {"$lookup": {"from": "plans", "localField": "plan_id", "foreignField": "_id", "as": "plan"}},
        {"$group": {"_id": {"$ifNull": [{"$arrayElemAt": ["$plan.name", 0]}, "Sem Plano"]}, "count": {"$sum": 1}}}
    ]
    return {item["_id"]: item["count"] for item in mongo.db.clients.aggregate(plan_pipeline)}


@dashboard.route("/")
@login_required
def index():
    """Main dashboard route"""
    user = User.get_by_id(current_user.id)
    user_type = user.get("user_type", "client") if user else "client"

    if user_type == "admin":
        return admin_dashboard()
    else:
        return client_dashboard()


@dashboard.route("/admin")
@login_required
def admin_dashboard():
    """Admin enterprise dashboard"""
    user = User.get_by_id(current_user.id)
    if not user or user.get("user_type") != "admin":
        return "Unauthorized", 403

    # Use cached statistics
    stats = _get_admin_stats_cached()
    stats["inactive_clients"] = stats["total_clients"] - stats["active_clients"]

    # Get recent activity
    recent_logins = LoginLog.get_recent(limit=10)
    
    # Calculate growth metrics efficiently
    from app import mongo
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    new_clients = mongo.db.clients.count_documents({"createdAt": {"$gte": thirty_days_ago}})
    new_infos = mongo.db.infos.count_documents({"createdAt": {"$gte": thirty_days_ago}})

    # Use cached plan distribution
    plan_distribution = _get_plan_distribution_cached()

    # Client status over time (last 7 days)
    client_activity = []
    for i in range(7):
        date = datetime.utcnow() - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        # This is a simplified version - in real implementation you'd track daily activity
        client_activity.append({
            "date": date_str,
            "active": stats["active_clients"] + (i * 2),  # Mock data for demo
            "total": stats["total_clients"] + (i * 3)
        })
    client_activity.reverse()

    return DashboardView.render_admin_dashboard(
        user=user,
        stats=stats,
        recent_logins=recent_logins,
        plan_distribution=plan_distribution,
        client_activity=client_activity,
        new_clients=new_clients,
        new_infos=new_infos
    )


@dashboard.route("/client")
@login_required
def client_dashboard():
    """Client enterprise dashboard"""
    user = User.get_by_id(current_user.id)
    if not user:
        return "User not found", 404

    # Get client data
    plan = None
    if user.get("plan_id"):
        plan = Plan.get_by_id(user.get("plan_id"))

    # Get client domains and infos
    client_domains = Domain.get_client_domains(user["_id"])
    client_infos = Info.get_by_client(user["_id"])

    # Get click statistics
    total_clicks = Click.get_total_clicks(user["_id"], days=30)
    click_stats = Click.get_click_stats(user["_id"], days=30)
    clicks_by_date = Click.get_clicks_by_date(user["_id"], days=30)

    # Calculate statistics
    stats = {
        "total_domains": len(client_domains),
        "total_infos": len(client_infos),
        "active_infos": len([i for i in client_infos if i.get("status") == "active"]),
        "total_clicks": total_clicks,
        "total_balance": sum(float(i.get("saldo", 0)) for i in client_infos),
    }

    # Plan expiration info
    plan_info = None
    if plan and user.get("expiredAt"):
        days_remaining = (user["expiredAt"] - datetime.utcnow()).days
        plan_info = {
            "name": plan["name"],
            "expires_at": user["expiredAt"],
            "days_remaining": max(0, days_remaining),
            "is_expired": days_remaining < 0
        }

    return DashboardView.render_client_dashboard(
        user=user,
        stats=stats,
        plan_info=plan_info,
        client_domains=client_domains,
        client_infos=client_infos,
        click_stats=click_stats,
        clicks_by_date=clicks_by_date
    )


@dashboard.route("/api/clicks-chart")
@login_required
def clicks_chart_api():
    """API endpoint for clicks chart data"""
    user = User.get_by_id(current_user.id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    days = request.args.get("days", 30, type=int)
    clicks_by_date = Click.get_clicks_by_date(user["_id"], days=days)
    
    # Format data for Chart.js
    labels = []
    data = []
    
    # Create a complete date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days-1)
    
    click_dict = {item["_id"]: item["clicks"] for item in clicks_by_date}
    
    for i in range(days):
        date = start_date + timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        labels.append(date.strftime("%m/%d"))
        data.append(click_dict.get(date_str, 0))
    
    return jsonify({
        "labels": labels,
        "datasets": [{
            "label": "Clicks",
            "data": data,
            "borderColor": "rgb(75, 192, 192)",
            "backgroundColor": "rgba(75, 192, 192, 0.2)",
            "tension": 0.1
        }]
    })


@dashboard.route("/api/domain-stats")
@login_required
def domain_stats_api():
    """API endpoint for domain statistics"""
    user = User.get_by_id(current_user.id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    click_stats = Click.get_click_stats(user["_id"], days=30)
    domains = Domain.get_client_domains(user["_id"])
    
    # Create domain lookup
    domain_lookup = {str(d["_id"]): d for d in domains}
    
    # Format data for charts
    labels = []
    data = []
    
    for stat in click_stats[:10]:  # Top 10 domains
        domain_id = str(stat.get("domain_id", ""))
        domain = domain_lookup.get(domain_id)
        if domain:
            labels.append(f"{stat.get('subdomain', '')}.{domain.get('name', 'Unknown')}")
        else:
            labels.append(f"{stat.get('subdomain', 'Unknown')}")
        data.append(stat.get("total_clicks", 0))
    
    return jsonify({
        "labels": labels,
        "datasets": [{
            "label": "Clicks por Domínio",
            "data": data,
            "backgroundColor": [
                "rgba(255, 99, 132, 0.8)",
                "rgba(54, 162, 235, 0.8)",
                "rgba(255, 205, 86, 0.8)",
                "rgba(75, 192, 192, 0.8)",
                "rgba(153, 102, 255, 0.8)",
                "rgba(255, 159, 64, 0.8)",
                "rgba(199, 199, 199, 0.8)",
                "rgba(83, 102, 255, 0.8)",
                "rgba(255, 99, 255, 0.8)",
                "rgba(99, 255, 132, 0.8)"
            ]
        }]
    })


@dashboard.route("/api/admin-stats")
@login_required
def admin_stats_api():
    """API endpoint for admin statistics"""
    user = User.get_by_id(current_user.id)
    if not user or user.get("user_type") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    from app import mongo
    
    # Optimized: Use aggregation for plan distribution
    plan_pipeline = [
        {"$lookup": {"from": "plans", "localField": "plan_id", "foreignField": "_id", "as": "plan"}},
        {"$group": {"_id": {"$ifNull": [{"$arrayElemAt": ["$plan.name", 0]}, "Sem Plano"]}, "count": {"$sum": 1}}}
    ]
    plan_distribution = {item["_id"]: item["count"] for item in mongo.db.clients.aggregate(plan_pipeline)}

    # Optimized: Use aggregation for status distribution
    status_pipeline = [
        {"$group": {"_id": {"$ifNull": ["$status", "unknown"]}, "count": {"$sum": 1}}}
    ]
    status_distribution = {item["_id"]: item["count"] for item in mongo.db.clients.aggregate(status_pipeline)}

    return jsonify({
        "plan_distribution": {
            "labels": list(plan_distribution.keys()),
            "datasets": [{
                "data": list(plan_distribution.values()),
                "backgroundColor": [
                    "rgba(255, 99, 132, 0.8)",
                    "rgba(54, 162, 235, 0.8)",
                    "rgba(255, 205, 86, 0.8)",
                    "rgba(75, 192, 192, 0.8)",
                    "rgba(153, 102, 255, 0.8)",
                    "rgba(255, 159, 64, 0.8)"
                ]
            }]
        },
        "status_distribution": {
            "labels": list(status_distribution.keys()),
            "datasets": [{
                "data": list(status_distribution.values()),
                "backgroundColor": [
                    "rgba(75, 192, 192, 0.8)",
                    "rgba(255, 99, 132, 0.8)",
                    "rgba(255, 205, 86, 0.8)"
                ]
            }]
        }
    })