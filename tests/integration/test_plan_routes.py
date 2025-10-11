"""
Integration tests for plan routes.
"""
from app.models.admin import Admin
from app.models.plan import Plan


class TestPlanRoutes:
    """Test cases for plan routes"""

    def test_list_plans_requires_auth(self, client):
        """Test that listing plans requires authentication"""
        response = client.get('/plans/', follow_redirects=True)
        assert response.status_code == 200
        assert b'login' in response.data.lower()

    def test_list_plans_as_admin(self, client, app):
        """Test listing plans as admin"""
        with app.app_context():
            # Create admin and plan
            Admin.create('testadmin', 'password123', 'admin')
            Plan.create('Test Plan', 'Description', 99.99, 30)

        # Login as admin
        client.post('/login', data={
            'username': 'testadmin',
            'password': 'password123'
        })

        # Access plans list
        response = client.get('/plans/')
        assert response.status_code == 200
        assert b'Test Plan' in response.data

    def test_create_plan_page_loads(self, client, app):
        """Test that create plan page loads for admin"""
        with app.app_context():
            Admin.create('testadmin', 'password123', 'admin')

        # Login
        client.post('/login', data={
            'username': 'testadmin',
            'password': 'password123'
        })

        # Access create page
        response = client.get('/plans/create')
        assert response.status_code == 200

    def test_create_plan_success(self, client, app):
        """Test successful plan creation"""
        with app.app_context():
            Admin.create('testadmin', 'password123', 'admin')

        # Login
        client.post('/login', data={
            'username': 'testadmin',
            'password': 'password123'
        })

        # Create plan
        response = client.post('/plans/create', data={
            'name': 'New Plan',
            'description': 'A new test plan',
            'price': '149.99',
            'duration_days': '60'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'successfully' in response.data.lower()

    def test_create_plan_missing_fields(self, client, app):
        """Test plan creation with missing fields"""
        with app.app_context():
            Admin.create('testadmin', 'password123', 'admin')

        # Login
        client.post('/login', data={
            'username': 'testadmin',
            'password': 'password123'
        })

        # Try to create plan without required fields
        response = client.post('/plans/create', data={
            'name': 'Incomplete Plan'
            # Missing price and duration
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'required' in response.data.lower() or b'fill' in response.data.lower()

    def test_edit_plan_success(self, client, app):
        """Test successful plan editing"""
        with app.app_context():
            Admin.create('testadmin', 'password123', 'admin')
            success, plan_id = Plan.create('Old Name', 'Old Desc', 99.99, 30)

        # Login
        client.post('/login', data={
            'username': 'testadmin',
            'password': 'password123'
        })

        # Edit plan
        response = client.post(f'/plans/edit/{plan_id}', data={
            'name': 'Updated Name',
            'description': 'Updated description',
            'price': '129.99',
            'duration_days': '45'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'successfully' in response.data.lower() or b'updated' in response.data.lower()

    def test_delete_plan_success(self, client, app):
        """Test successful plan deletion"""
        with app.app_context():
            Admin.create('testadmin', 'password123', 'admin')
            success, plan_id = Plan.create('To Delete', 'Description', 99.99, 30)

        # Login
        client.post('/login', data={
            'username': 'testadmin',
            'password': 'password123'
        })

        # Delete plan
        response = client.post(f'/plans/delete/{plan_id}', follow_redirects=True)

        assert response.status_code == 200
        assert b'deleted' in response.data.lower() or b'successfully' in response.data.lower()

    def test_view_plan_details(self, client, app):
        """Test viewing plan details"""
        with app.app_context():
            Admin.create('testadmin', 'password123', 'admin')
            success, plan_id = Plan.create('View Plan', 'Test Description', 99.99, 30)

        # Login
        client.post('/login', data={
            'username': 'testadmin',
            'password': 'password123'
        })

        # View plan
        response = client.get(f'/plans/view/{plan_id}')

        assert response.status_code == 200
        assert b'View Plan' in response.data
        assert b'99.99' in response.data or b'99' in response.data
