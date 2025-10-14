from app.views.base_view import BaseView


class MainView(BaseView):
    """
    View class for main routes like index and dashboard.
    """

    @staticmethod
    def render_index(plans=None):
        """
        Render the index page.

        Returns:
            str: Rendered index template
        """
        formatted_plans = MainView._prepare_plan_cards(plans or [])
        return BaseView.render("index.html", plans=formatted_plans)

    @staticmethod
    def _prepare_plan_cards(plans):
        """Normalize plan information for the pricing section."""
        if not plans:
            return []

        def format_price_brl(value):
            try:
                number = float(value)
                return f"R${number:,.0f}".replace(",", ".")
            except Exception:
                return f"R${value}"

        formatted = []

        def price_key(plan):
            try:
                return float(plan.get("price", 0))
            except (ValueError, TypeError):
                return 0

        sorted_plans = sorted(plans, key=price_key)

        for index, plan in enumerate(sorted_plans):
            slug = plan.get("slug") or plan.get("name", "").lower().replace(" ", "-")

            raw_duration = plan.get("duration_days") or plan.get("duration", 0)
            try:
                duration = int(raw_duration)
            except (ValueError, TypeError):
                duration = 0

            features = plan.get("features", [])
            if isinstance(features, str):
                features = [item.strip() for item in features.split("\n") if item.strip()]

            formatted.append(
                {
                    "name": plan.get("name", ""),
                    "description": plan.get("description", ""),
                    "price_display": format_price_brl(plan.get("price", 0)),
                    "duration_label": f"{duration} dias" if duration else "",
                    "features": features,
                    "slug": slug,
                    "is_featured": slug == "growth",
                    "button_style": "primary" if slug == "growth" else "outline-primary",
                    "animation_delay": f"{index * 0.1:.1f}s" if index else None,
                    "badge": "MAIS POPULAR" if slug == "growth" else None,
                }
            )

        return formatted

    @staticmethod
    def render_dashboard(user, **context):
        """
        Render the dashboard page.

        Args:
            user (dict): User data dictionary
            **context: Additional context variables

        Returns:
            str: Rendered dashboard template
        """
        # Combine user with other context variables
        context["user"] = user

        return BaseView.render("dashboard.html", **context)
