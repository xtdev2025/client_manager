from app.views.base_view import BaseView


class DashboardView(BaseView):
    """View class for dashboard templates"""

    @staticmethod
    def render_admin_dashboard(user, stats, recent_logins, plan_distribution, 
                             client_activity, new_clients, new_infos, recent_clicks=None, payout_insights=None):
        """Render admin enterprise dashboard using dashboard.html with admin.html fragment"""
        # Map stats to individual variables for admin.html template compatibility
        default_payout_summary = {
            "period_days": 30,
            "total_count": 0,
            "total_amount": 0.0,
            "pending": {"count": 0, "amount": 0.0},
            "confirmed": {"count": 0, "amount": 0.0},
            "failed": {"count": 0, "amount": 0.0},
            "confirmation_rate": 0.0,
            "pending_rate": 0.0,
            "failed_rate": 0.0,
        }
        payout_context = payout_insights or {}
        summary = payout_context.get("summary") or default_payout_summary

        context = {
            "user": user,
            "user_type": "admin",
            "stats": stats,
            "recent_logins": recent_logins,  # Template expects this name
            "plan_distribution": plan_distribution,
            "client_activity": client_activity,
            "new_clients": new_clients,
            "new_infos": new_infos,
            "recent_clicks": recent_clicks or [],
            "payout_insights": {
                "summary": summary,
                "distribution": payout_context.get("distribution", {}),
                "raw_stats": payout_context.get("raw_stats", {}),
            },
            # Legacy variable names for backward compatibility
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
            "infos_detailed": [],
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