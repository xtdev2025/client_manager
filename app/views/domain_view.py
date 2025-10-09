from app.views.base_view import BaseView

class DomainView(BaseView):
    """
    View class for domain-related templates.
    """
    
    @staticmethod
    def render_list(domains):
        """
        Render the domain list page.
        
        Args:
            domains (list): List of domain dictionaries
            
        Returns:
            str: Rendered domain list template
        """
        return BaseView.render('domains/list.html', domains=domains)
    
    @staticmethod
    def render_create_form(form_data=None, errors=None):
        """
        Render the domain creation form.
        
        Args:
            form_data (dict, optional): Form data in case of validation error
            errors (list, optional): Validation errors
            
        Returns:
            str: Rendered domain creation form
        """
        return BaseView.render(
            'domains/create.html',
            form_data=form_data,
            errors=errors
        )
    
    @staticmethod
    def render_edit_form(domain_data, errors=None):
        """
        Render the domain edit form.
        
        Args:
            domain_data (dict): Domain data to edit
            errors (list, optional): Validation errors
            
        Returns:
            str: Rendered domain edit form
        """
        return BaseView.render(
            'domains/edit.html',
            domain=domain_data,
            errors=errors
        )
    
    @staticmethod
    def render_view(domain_data, client_domains=None):
        """
        Render the domain view page.
        
        Args:
            domain_data (dict): Domain data to view
            client_domains (list, optional): List of clients using this domain
            
        Returns:
            str: Rendered domain view template
        """
        return BaseView.render(
            'domains/view.html', 
            domain=domain_data,
            client_domains=client_domains or []
        )