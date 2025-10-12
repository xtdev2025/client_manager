from app.views.base_view import BaseView


class DashboardView(BaseView):
    """View class for dashboard templates"""

    @staticmethod
    def render_admin_dashboard(user, stats, recent_logins, plan_distribution, 
                             client_activity, new_clients, new_infos):
        """Render admin enterprise dashboard"""
        return BaseView.render(
            "dashboard/admin_enterprise.html",
            user=user,
            stats=stats,
            recent_logins=recent_logins,
            plan_distribution=plan_distribution,
            client_activity=client_activity,
            new_clients=new_clients,
            new_infos=new_infos
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

    @staticmethod
    def render_simple_dashboard(user, stats, recent_logins=None, plan_info=None, client_domains=None):
        """Render simple dashboard"""
        return BaseView.render(
            "dashboard/simple.html",
            user=user,
            stats=stats,
            recent_logins=recent_logins,
            plan_info=plan_info,
            client_domains=client_domains
        )