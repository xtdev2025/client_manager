from app.views.base_view import BaseView

class AuthView(BaseView):
    """
    View class for authentication-related templates.
    """
    
    @staticmethod
    def render_login(form_data=None, errors=None):
        """
        Render the login page.
        
        Args:
            form_data (dict, optional): Form data in case of validation error
            errors (list, optional): Validation errors
            
        Returns:
            str: Rendered login template
        """
        return BaseView.render(
            'auth/login.html',
            form_data=form_data,
            errors=errors
        )
    
    @staticmethod
    def render_register(form_data=None, errors=None):
        """
        Render the client registration page.
        
        Args:
            form_data (dict, optional): Form data in case of validation error
            errors (list, optional): Validation errors
            
        Returns:
            str: Rendered registration template
        """
        return BaseView.render(
            'auth/register.html',
            form_data=form_data,
            errors=errors
        )
    
    @staticmethod
    def render_register_admin(form_data=None, errors=None):
        """
        Render the admin registration page.
        
        Args:
            form_data (dict, optional): Form data in case of validation error
            errors (list, optional): Validation errors
            
        Returns:
            str: Rendered admin registration template
        """
        return BaseView.render(
            'auth/register_admin.html',
            form_data=form_data,
            errors=errors
        )