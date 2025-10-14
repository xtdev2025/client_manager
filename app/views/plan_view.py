from app.views.base_view import BaseView


class PlanView(BaseView):
    """
    View class for plan-related templates.
    """

    @staticmethod
    def render_list(plans):
        """
        Render the plan list page.

        Args:
            plans (list): List of plan dictionaries

        Returns:
            str: Rendered plan list template
        """
        return BaseView.render("plans/list.html", plans=plans)

    @staticmethod
    def render_create_form(form_data=None, errors=None):
        """
        Render the plan creation form.

        Args:
            form_data (dict, optional): Form data in case of validation error
            errors (list, optional): Validation errors

        Returns:
            str: Rendered plan creation form
        """
        return BaseView.render_form("plans/create.html", form_data=form_data, errors=errors)

    @staticmethod
    def render_edit_form(plan_data, errors=None):
        """
        Render the plan edit form.

        Args:
            plan_data (dict): Plan data to edit
            errors (list, optional): Validation errors

        Returns:
            str: Rendered plan edit form
        """
        return BaseView.render_form("plans/edit.html", form_data=plan_data, errors=errors, plan=plan_data)

    @staticmethod
    def render_view(plan_data):
        """
        Render the plan view page.

        Args:
            plan_data (dict): Plan data to view

        Returns:
            str: Rendered plan view template
        """
        return BaseView.render("plans/view.html", plan=plan_data)
