from app.views.base_view import BaseView

class MainView(BaseView):
    """
    View class for main routes like index and dashboard.
    """
    
    @staticmethod
    def render_index():
        """
        Render the index page.
        
        Returns:
            str: Rendered index template
        """
        return BaseView.render('index.html')
    
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
        context['user'] = user
        
        return BaseView.render('dashboard.html', **context)