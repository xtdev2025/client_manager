"""
Unit tests for ClientService.
"""
import pytest
from app.services.client_service import ClientService
from app.models.plan import Plan
from app.models.client import Client


class TestClientService:
    """Test cases for ClientService"""
    
    def test_validate_client_data_success(self, app):
        """Test successful validation of client data"""
        with app.app_context():
            # Create a plan first
            success, plan_id = Plan.create('Test Plan', 'Test Description', 99.99, 30)
            assert success is True
            
            # Validate client data
            valid, error = ClientService.validate_client_data(
                'testclient', 'password123', plan_id, 'active'
            )
            assert valid is True
            assert error is None
    
    def test_validate_client_data_missing_username(self, app):
        """Test validation fails with missing username"""
        with app.app_context():
            success, plan_id = Plan.create('Test Plan', 'Test Description', 99.99, 30)
            
            valid, error = ClientService.validate_client_data('', 'password123', plan_id)
            assert valid is False
            assert 'required' in error.lower()
    
    def test_validate_client_data_missing_plan(self, app):
        """Test validation fails with missing plan"""
        with app.app_context():
            valid, error = ClientService.validate_client_data('testclient', 'password123', '')
            assert valid is False
            assert 'required' in error.lower()
    
    def test_validate_client_data_nonexistent_plan(self, app):
        """Test validation fails with nonexistent plan"""
        with app.app_context():
            valid, error = ClientService.validate_client_data(
                'testclient', 'password123', '507f1f77bcf86cd799439011'
            )
            assert valid is False
            assert 'does not exist' in error.lower()
    
    def test_validate_client_data_invalid_status(self, app):
        """Test validation fails with invalid status"""
        with app.app_context():
            success, plan_id = Plan.create('Test Plan', 'Test Description', 99.99, 30)
            
            valid, error = ClientService.validate_client_data(
                'testclient', 'password123', plan_id, 'invalid_status'
            )
            assert valid is False
            assert 'invalid status' in error.lower()
    
    def test_get_client_with_details(self, app):
        """Test getting client with enriched details"""
        with app.app_context():
            # Create plan and client
            success, plan_id = Plan.create('Test Plan', 'Test Description', 99.99, 30)
            success, client_id = Client.create('testclient', 'password123', plan_id)
            
            # Get client with details
            client = ClientService.get_client_with_details(client_id)
            
            assert client is not None
            assert 'plan' in client
            assert client['plan']['name'] == 'Test Plan'
    
    def test_get_client_with_details_nonexistent(self, app):
        """Test getting nonexistent client returns None"""
        with app.app_context():
            client = ClientService.get_client_with_details('507f1f77bcf86cd799439011')
            assert client is None
    
    def test_get_clients_with_plan_info(self, app):
        """Test getting all clients with plan information"""
        with app.app_context():
            # Create plan and multiple clients
            success, plan_id = Plan.create('Test Plan', 'Test Description', 99.99, 30)
            Client.create('client1', 'password123', plan_id)
            Client.create('client2', 'password123', plan_id)
            
            # Get all clients
            clients = ClientService.get_clients_with_plan_info()
            
            assert len(clients) == 2
            assert all('plan' in client for client in clients)
    
    def test_update_client_plan(self, app):
        """Test updating client plan"""
        with app.app_context():
            # Create plans and client
            success, plan1_id = Plan.create('Plan 1', 'Description 1', 50.00, 30)
            success, plan2_id = Plan.create('Plan 2', 'Description 2', 100.00, 60)
            success, client_id = Client.create('testclient', 'password123', plan1_id)
            
            # Update client plan
            success, message = ClientService.update_client_plan(client_id, plan2_id)
            
            assert success is True
            
            # Verify plan was updated
            client = Client.get_by_id(client_id)
            assert str(client['plan_id']) == plan2_id
