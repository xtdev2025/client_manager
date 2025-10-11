from datetime import datetime, timedelta

from app.views.base_view import BaseView
from app.models.plan import Plan
from app.models.template import Template
from app.models.domain import Domain
from app.models.info import Info

class ClientView(BaseView):
    """
    View class for client-related templates.
    """

    @staticmethod
    def _enrich_plan_metadata(client):
        """Populate plan-related fields such as plan object, name, and expiration."""
        plan = None
        if client.get('plan_id'):
            plan = Plan.get_by_id(client['plan_id'])

        client['plan'] = plan
        client['plan_name'] = plan['name'] if plan else 'No Plan'

        if plan and not client.get('planActivatedAt'):
            activation_candidate = client.get('planActivatedAt') or client.get('updatedAt') or client.get('createdAt')
            if isinstance(activation_candidate, datetime):
                client['planActivatedAt'] = activation_candidate

        if not client.get('expiredAt') and plan and plan.get('duration_days'):
            activation = client.get('planActivatedAt')
            if isinstance(activation, datetime):
                client['expiredAt'] = activation + timedelta(days=plan.get('duration_days'))

        return client
    
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
            ClientView._enrich_plan_metadata(client)
            # Add info count
            client['info_count'] = Info.count_by_client(client['_id'])
        
        return BaseView.render('clients/list.html', clients=clients)
    
    @staticmethod
    def render_create_form(plans, templates=None, form_data=None, errors=None):
        """
        Render the client creation form.
        
        Args:
            plans (list): List of available plans
            templates (list): List of available templates
            form_data (dict, optional): Form data in case of validation error
            errors (list, optional): Validation errors
            
        Returns:
            str: Rendered client creation form
        """
        return BaseView.render(
            'clients/create.html',
            plans=plans,
            templates=templates or [],
            form_data=form_data,
            errors=errors
        )
    
    @staticmethod
    def render_edit_form(client_data, plans, templates=None, form_data=None, errors=None):
        """
        Render the client edit form.
        
        Args:
            client_data (dict): Client data to edit
            plans (list): List of available plans
            templates (list): List of available templates
            errors (list, optional): Validation errors
            
        Returns:
            str: Rendered client edit form
        """
        ClientView._enrich_plan_metadata(client_data)

        return BaseView.render(
            'clients/edit.html',
            client=client_data,
            plans=plans,
            templates=templates or [],
            form_data=form_data,
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
        ClientView._enrich_plan_metadata(client_data)
            
        # Enrich client data with template information
        if 'template_id' in client_data and client_data['template_id']:
            template = Template.get_by_id(client_data['template_id'])
            client_data['template_name'] = template['name'] if template else 'No Template'
            client_data['template'] = template
        else:
            client_data['template_name'] = 'No Template'
            
        # Get client domains
        client_domains = Domain.get_client_domains(client_data['_id'])
        client_data['domains'] = client_domains
        
        # Get client infos
        client_infos = Info.get_by_client(client_data['_id'])
        client_data['infos'] = client_infos
        client_data['info_count'] = len(client_infos)
        
        return BaseView.render('clients/view.html', client=client_data)
        
    @staticmethod
    def render_domains(client_data, client_domains, available_domains, domain_limit):
        """
        Render the client domains management page.
        
        Args:
            client_data (dict): Client data
            client_domains (list): List of domains assigned to the client
            available_domains (list): List of all available domains
            domain_limit (int): Maximum number of domains allowed for this client
            
        Returns:
            str: Rendered client domains template
        """
        return BaseView.render(
            'clients/domains.html',
            client=client_data,
            client_domains=client_domains,
            available_domains=available_domains,
            domain_limit=domain_limit
        )