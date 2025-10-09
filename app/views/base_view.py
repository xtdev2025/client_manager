from flask import render_template
from datetime import datetime

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
        if 'now' not in context:
            context['now'] = datetime.now()
            
        return render_template(template_path, **context)