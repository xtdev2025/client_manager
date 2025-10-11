"""
Client service for handling client business logic.
"""
from typing import Optional, Tuple, Dict, Any, List
from datetime import datetime
from bson import ObjectId
from app.models.client import Client
from app.models.plan import Plan
from app.models.template import Template
from app import mongo


class ClientService:
    """Service class for client operations"""
    
    @staticmethod
    def validate_client_data(username: str, password: str, plan_id: str,
                            status: str = 'active') -> Tuple[bool, Optional[str]]:
        """
        Validate client creation data.
        
        Args:
            username: The username for the client
            password: The password for the client
            plan_id: The plan ID to assign
            status: The status of the client (active/inactive)
            
        Returns:
            Tuple containing:
                - valid: bool indicating if data is valid
                - error_message: str with error message if invalid, None otherwise
        """
        if not username or not password:
            return False, "Username and password are required"
        
        if not plan_id:
            return False, "Plan selection is required"
        
        # Validate plan exists
        plan = Plan.get_by_id(plan_id)
        if not plan:
            return False, "Selected plan does not exist"
        
        # Validate status
        if status not in ['active', 'inactive']:
            return False, "Invalid status. Must be 'active' or 'inactive'"
        
        return True, None
    
    @staticmethod
    def get_client_with_details(client_id: str) -> Optional[Dict[str, Any]]:
        """
        Get client data enriched with plan and template information.
        
        Args:
            client_id: The client ID
            
        Returns:
            Dict with client data or None if not found
        """
        client = Client.get_by_id(client_id)
        if not client:
            return None
        
        # Enrich with plan information
        if 'plan_id' in client and client['plan_id']:
            plan = Plan.get_by_id(client['plan_id'])
            if plan:
                client['plan'] = plan
        
        # Enrich with template information
        if 'template_id' in client and client['template_id']:
            template = Template.get_by_id(client['template_id'])
            if template:
                client['template'] = template
        
        return client
    
    @staticmethod
    def get_clients_with_plan_info() -> List[Dict[str, Any]]:
        """
        Get all clients enriched with their plan information.
        
        Returns:
            List of client dicts with plan data
        """
        clients = Client.get_all()
        
        for client in clients:
            if 'plan_id' in client and client['plan_id']:
                plan = Plan.get_by_id(client['plan_id'])
                if plan:
                    client['plan'] = plan
        
        return clients
    
    @staticmethod
    def update_client_plan(client_id: str, plan_id: str,
                          activation_date: Optional[str] = None,
                          expiration_date: Optional[str] = None) -> Tuple[bool, str]:
        """
        Update a client's plan assignment.
        
        Args:
            client_id: The client ID
            plan_id: The new plan ID
            activation_date: Optional activation date
            expiration_date: Optional expiration date
            
        Returns:
            Tuple containing:
                - success: bool indicating if update succeeded
                - message: str with success/error message
        """
        # Validate plan exists
        plan = Plan.get_by_id(plan_id)
        if not plan:
            return False, "Selected plan does not exist"
        
        # Update client
        update_data = {
            'plan_id': ObjectId(plan_id) if isinstance(plan_id, str) else plan_id
        }
        
        if activation_date:
            update_data['planActivatedAt'] = activation_date
        if expiration_date:
            update_data['expiredAt'] = expiration_date
        
        return Client.update(client_id, update_data)
    
    @staticmethod
    def check_client_plan_expiration(client_id: str) -> Tuple[bool, Optional[datetime], Optional[int]]:
        """
        Check if a client's plan is expired or expiring soon.
        
        Args:
            client_id: The client ID
            
        Returns:
            Tuple containing:
                - is_expired: bool indicating if plan is expired
                - expiration_date: datetime of expiration or None
                - days_remaining: int days until expiration or None
        """
        client = Client.get_by_id(client_id)
        if not client:
            return False, None, None
        
        expiration_date = client.get('expiredAt')
        if not expiration_date:
            return False, None, None
        
        now = datetime.utcnow()
        
        if expiration_date < now:
            return True, expiration_date, 0
        
        days_remaining = (expiration_date - now).days
        return False, expiration_date, days_remaining
