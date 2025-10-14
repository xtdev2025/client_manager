from datetime import datetime

from flask import render_template


class BaseView:
    """
    Base class for all views in the application.
    Provides common functionality for rendering templates.
    """

    @staticmethod
    def render(template_path, **context):
        """
        Render a template with the given context.
        Always includes the current datetime as 'now' in the context.

        Args:
            template_path (str): Path to the template relative to templates folder
            **context: Additional context variables to pass to the template

        Returns:
            str: Rendered template
        """
        # Always include datetime in context
        if "now" not in context:
            context["now"] = datetime.now()

        return render_template(template_path, **context)

    @classmethod
    def render_form(cls, template_path, form_data=None, errors=None, **extra_context):
        """
        Render a form template with common form context.

        Args:
            template_path (str): Path to the form template
            form_data (dict, optional): Form data for pre-filling
            errors (list, optional): Validation errors
            **extra_context: Additional context variables

        Returns:
            str: Rendered template
        """
        context = {
            "form_data": form_data or {},
            "errors": errors or [],
            **extra_context
        }
        return cls.render(template_path, **context)

    @classmethod
    def render_table(cls, template_path, items, **extra_context):
        """
        Render a table/list template with items.

        Args:
            template_path (str): Path to the table template
            items (list): List of items to display
            **extra_context: Additional context variables

        Returns:
            str: Rendered template
        """
        context = {
            "items": items,
            **extra_context
        }
        return cls.render(template_path, **context)
