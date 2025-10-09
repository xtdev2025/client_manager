from app.views.base_view import BaseView

class TemplateView(BaseView):
    """
    View class for template-related templates.
    """
    
    @staticmethod
    def render_list(templates):
        """
        Render the template list page.
        
        Args:
            templates (list): List of template dictionaries
            
        Returns:
            str: Rendered template list template
        """
        return BaseView.render('templates/list.html', templates=templates)
    
    @staticmethod
    def render_create_form(form_data=None, errors=None):
        """
        Render the template creation form.
        
        Args:
            form_data (dict, optional): Form data in case of validation error
            errors (list, optional): Validation errors
            
        Returns:
            str: Rendered template creation form
        """
        return BaseView.render(
            'templates/create.html',
            form_data=form_data,
            errors=errors
        )
    
    @staticmethod
    def render_edit_form(template_data, errors=None):
        """
        Render the template edit form.
        
        Args:
            template_data (dict): Template data to edit
            errors (list, optional): Validation errors
            
        Returns:
            str: Rendered template edit form
        """
        return BaseView.render(
            'templates/edit.html',
            template=template_data,
            errors=errors
        )
    
    @staticmethod
    def render_view(template_data):
        """
        Render the template view page.
        
        Args:
            template_data (dict): Template data to view
            
        Returns:
            str: Rendered template view template
        """
        return BaseView.render('templates/view.html', template=template_data)