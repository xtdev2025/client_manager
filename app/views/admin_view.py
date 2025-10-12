from app.views.base_view import BaseView


class AdminView(BaseView):
    """
    View class for admin-related templates.
    """

    @staticmethod
    def render_list(admins):
        """
        Render the admin list page.

        Args:
            admins (list): List of admin dictionaries

        Returns:
            str: Rendered admin list template
        """
        return BaseView.render("admins/list.html", admins=admins)

    @staticmethod
    def render_create_form(form_data=None, errors=None):
        """
        Render the admin creation form.

        Args:
            form_data (dict, optional): Form data in case of validation error
            errors (list, optional): Validation errors

        Returns:
            str: Rendered admin creation form
        """
        return BaseView.render("admins/create.html", form_data=form_data, errors=errors)

    @staticmethod
    def render_edit_form(admin_data, errors=None):
        """
        Render the admin edit form.

        Args:
            admin_data (dict): Admin data to edit
            errors (list, optional): Validation errors

        Returns:
            str: Rendered admin edit form
        """
        return BaseView.render("admins/edit.html", admin=admin_data, errors=errors)

    @staticmethod
    def render_profile(admin_data, errors=None):
        """
        Render the admin profile page.

        Args:
            admin_data (dict): Admin data to view
            errors (list, optional): Validation errors

        Returns:
            str: Rendered admin profile template
        """
        return BaseView.render("admins/profile.html", admin=admin_data, errors=errors)

    @staticmethod
    def render_audit_logs(logs, admins, total, page, total_pages, per_page, filters):
        """
        Render the audit logs page with filters and pagination.

        Args:
            logs (list): List of audit log entries
            admins (list): List of admins for filter dropdown
            total (int): Total number of logs
            page (int): Current page number
            total_pages (int): Total number of pages
            per_page (int): Number of logs per page
            filters (dict): Current filter values

        Returns:
            str: Rendered audit logs template
        """
        return BaseView.render(
            "admins/audit_logs.html",
            logs=logs,
            admins=admins,
            total=total,
            page=page,
            total_pages=total_pages,
            per_page=per_page,
            filters=filters,
        )
