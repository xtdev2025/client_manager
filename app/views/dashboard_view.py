from app.views.base_view import BaseView
from app.views.main_view import MainView


class DashboardView(BaseView):
    """View class for dashboard templates"""

    @staticmethod
    def render_admin_dashboard(user, stats, recent_logins, plan_distribution, 
                             client_activity, new_clients, new_infos, recent_clicks=None):
        """Render admin enterprise dashboard using dashboard.html with admin.html fragment"""
        # Map stats to individual variables for admin.html template compatibility
        context = {
            "user": user,
            "user_type": "admin",
            "client_count": stats.get("total_clients", 0),
            "active_clients": stats.get("active_clients", 0),
            "plan_count": stats.get("total_plans", 0),
            "domain_count": stats.get("total_domains", 0),
            "admin_count": stats.get("total_admins", 0),
            "info_count": stats.get("total_infos", 0),
            "active_infos": stats.get("active_infos", 0),
            "template_count": stats.get("total_templates", 0),
            "total_clicks": stats.get("total_clicks", 0),
            "recent_login_logs": recent_logins,
            "infos_detailed": [],  # Will be populated below if needed
            "plan_distribution": plan_distribution,
            "client_activity": client_activity,
            "new_clients": new_clients,
            "new_infos": new_infos,
            "recent_clicks": recent_clicks or []
        }
        
        return BaseView.render(
            "dashboard/admin_enterprise.html",
            **context
        )

    @staticmethod
    def render_client_dashboard(user, stats, plan_info, client_domains, 
                              client_infos, click_stats, clicks_by_date):
        """Render client enterprise dashboard"""
        return BaseView.render(
            "dashboard/client_enterprise.html",
            user=user,
            stats=stats,
            plan_info=plan_info,
            client_domains=client_domains,
            client_infos=client_infos,
            click_stats=click_stats,
            clicks_by_date=clicks_by_date
        )