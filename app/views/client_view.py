from app.views.base_view import BaseView
from app.models.plan import Plan

class ClientView(BaseView):
    """
    View class for client-related templates.
    """
    
    @staticmethod
    def render_list(clients):
        """
        Render the client list page.
        
        Args:
            clients (list): List of client dictionaries
            
        Returns:
            str: Rendered client list template
        """
        # Enrich client data with plan information before rendering
        for client in clients:
            if 'plan_id' in client and client['plan_id']:
                plan = Plan.get_by_id(client['plan_id'])
                client['plan_name'] = plan['name'] if plan else 'No Plan'
            else:
                client['plan_name'] = 'No Plan'
        
        return BaseView.render('clients/list.html', clients=clients)
    
    @staticmethod
    def render_create_form(plans, form_data=None, errors=None):
        """
        Render the client creation form.
        
        Args:
            plans (list): List of available plans
            form_data (dict, optional): Form data in case of validation error
            errors (list, optional): Validation errors
            
        Returns:
            str: Rendered client creation form
        """
        return BaseView.render(
            'clients/create.html',
            plans=plans,
            form_data=form_data,
            errors=errors
        )
    
    @staticmethod
    def render_edit_form(client_data, plans, errors=None):
        """
        Render the client edit form.
        
        Args:
            client_data (dict): Client data to edit
            plans (list): List of available plans
            errors (list, optional): Validation errors
            
        Returns:
            str: Rendered client edit form
        """
        return BaseView.render(
            'clients/edit.html',
            client=client_data,
            plans=plans,
            errors=errors
        )
    
    @staticmethod
    def render_view(client_data):
        """
        Render the client view page.
        
        Args:
            client_data (dict): Client data to view
            
        Returns:
            str: Rendered client view template
        """
        # Enrich client data with plan information
        if 'plan_id' in client_data and client_data['plan_id']:
            plan = Plan.get_by_id(client_data['plan_id'])
            client_data['plan_name'] = plan['name'] if plan else 'No Plan'
            client_data['plan'] = plan
        else:
            client_data['plan_name'] = 'No Plan'
            
        return BaseView.render('clients/view.html', client=client_data)