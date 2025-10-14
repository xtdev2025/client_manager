"""
Parametrized tests for CRUD scaffolding - ensuring CrudControllerMixin works correctly
for each entity (domain, client, plan, template, info).
"""
import pytest
from unittest.mock import MagicMock, patch

from app.controllers.crud_mixin import CrudControllerMixin
from app.repositories.base import CrudRepositoryProtocol
from app.utils.crud import CrudOperationResult


class MockCrudRepository(CrudRepositoryProtocol):
    """Mock repository that mimics ModelCrudRepository behavior"""

    def __init__(self, entity_name):
        self.entity_name = entity_name
        self.items = [
            {"_id": "1", "name": f"{entity_name} 1"},
            {"_id": "2", "name": f"{entity_name} 2"},
        ]

    def get_all(self):
        return CrudOperationResult.ok(self.items)

    def get_by_id(self, entity_id: str):
        item = next((item for item in self.items if str(item["_id"]) == entity_id), None)
        return item

    def create(self, data):
        new_item = {"_id": str(len(self.items) + 1), **data}
        self.items.append(new_item)
        return CrudOperationResult.ok(new_item, message="Created successfully")

    def update(self, entity_id: str, data):
        item = next((item for item in self.items if str(item["_id"]) == entity_id), None)
        if item:
            item.update(data)
            return CrudOperationResult.ok(item, message="Updated successfully")
        return CrudOperationResult.fail("Not found")

    def delete(self, entity_id: str):
        item = next((item for item in self.items if str(item["_id"]) == entity_id), None)
        if item:
            self.items.remove(item)
            return CrudOperationResult.ok(None, message="Deleted successfully")
        return CrudOperationResult.fail("Not found")


class MockView:
    """Mock view class with render methods"""

    @staticmethod
    def render_list(items):
        # items is CrudOperationResult
        return f"rendered list with {len(items.data)} items"

    @staticmethod
    def render_create_form(**kwargs):
        return "rendered create form"

    @staticmethod
    def render_edit_form(entity, **kwargs):
        return "rendered edit form"


# Mock controller classes to avoid import issues
class MockDomainController(CrudControllerMixin):
    entity_name = "Domain"
    audit_entity = "domain"
    list_endpoint = "domain.list_domains"
    create_schema = None
    update_schema = None
    view = MockView


class MockClientController(CrudControllerMixin):
    entity_name = "Client"
    audit_entity = "client"
    list_endpoint = "client.list_clients"
    create_schema = None
    update_schema = None
    view = MockView


class MockPlanController(CrudControllerMixin):
    entity_name = "Plan"
    audit_entity = "plan"
    list_endpoint = "plan.list_plans"
    create_schema = None
    update_schema = None
    view = MockView


class MockTemplateController(CrudControllerMixin):
    entity_name = "Template"
    audit_entity = "template"
    list_endpoint = "template.list_templates"
    create_schema = None
    update_schema = None
    view = MockView


class MockInfoController(CrudControllerMixin):
    entity_name = "Info"
    audit_entity = "info"
    list_endpoint = "info.list_infos"
    create_schema = None
    update_schema = None
    view = MockView


@pytest.mark.parametrize("controller_class,entity_name,audit_entity", [
    (MockDomainController, "Domain", "domain"),
    (MockClientController, "Client", "client"),
    (MockPlanController, "Plan", "plan"),
    (MockTemplateController, "Template", "template"),
    (MockInfoController, "Info", "info"),
])
class TestCrudScaffolding:
    """Parametrized tests ensuring CRUD scaffolding works for each entity"""

    def test_list_view_renders_correctly(self, controller_class, entity_name, audit_entity):
        """Test that list_view calls repository and renders with view"""
        mock_repo = MockCrudRepository(entity_name.lower())
        controller = controller_class(repository=mock_repo)

        with patch('app.controllers.crud_mixin.flash') as mock_flash:
            result = controller.list_view()

        assert result == f"rendered list with 2 items"
        mock_flash.assert_not_called()

    def test_create_view_get_request(self, controller_class, entity_name, audit_entity):
        """Test create_view handles GET request correctly"""
        mock_repo = MockCrudRepository(entity_name.lower())
        controller = controller_class(repository=mock_repo)

        with patch('app.controllers.crud_mixin.request') as mock_request, \
             patch('app.controllers.crud_mixin.flash') as mock_flash:
            mock_request.method = 'GET'

            result = controller.create_view()

        assert result == "rendered create form"
        mock_flash.assert_not_called()

    def test_create_view_post_success(self, controller_class, entity_name, audit_entity):
        """Test create_view handles successful POST request"""
        mock_repo = MockCrudRepository(entity_name.lower())
        controller = controller_class(repository=mock_repo)

        # Mock request.form as an object with to_dict method
        mock_form = MagicMock()
        mock_form.to_dict.return_value = {"name": f"New {entity_name}"}

        with patch('app.controllers.crud_mixin.request') as mock_request, \
             patch('app.controllers.crud_mixin.flash') as mock_flash, \
             patch('app.controllers.crud_mixin.redirect') as mock_redirect, \
             patch('app.controllers.crud_mixin.log_creation') as mock_log:
            mock_request.method = 'POST'
            mock_request.form = mock_form

            result = controller.create_view()

        mock_log.assert_called_once()
        mock_flash.assert_called_once_with("Created successfully", "success")
        mock_redirect.assert_called_once()

    def test_edit_view_get_success(self, controller_class, entity_name, audit_entity):
        """Test edit_view handles GET request for existing entity"""
        mock_repo = MockCrudRepository(entity_name.lower())
        controller = controller_class(repository=mock_repo)

        with patch('app.controllers.crud_mixin.flash') as mock_flash:
            result = controller.edit_view(entity_id="1")

        assert result == "rendered edit form"
        mock_flash.assert_not_called()

    def test_edit_view_entity_not_found(self, controller_class, entity_name, audit_entity):
        """Test edit_view handles non-existent entity"""
        mock_repo = MockCrudRepository(entity_name.lower())
        controller = controller_class(repository=mock_repo)

        with patch('app.controllers.crud_mixin.flash') as mock_flash, \
             patch('app.controllers.crud_mixin.redirect') as mock_redirect:
            result = controller.edit_view(entity_id="999")

        mock_flash.assert_called_once_with(f"{entity_name} not found", "danger")
        mock_redirect.assert_called_once()

    def test_delete_view_success(self, controller_class, entity_name, audit_entity):
        """Test delete_view handles successful deletion"""
        mock_repo = MockCrudRepository(entity_name.lower())
        controller = controller_class(repository=mock_repo)

        with patch('app.controllers.crud_mixin.request') as mock_request, \
             patch('app.controllers.crud_mixin.flash') as mock_flash, \
             patch('app.controllers.crud_mixin.redirect') as mock_redirect, \
             patch('app.controllers.crud_mixin.log_deletion') as mock_log:
            mock_request.method = 'POST'

            result = controller.delete_view(entity_id="1")

        mock_log.assert_called_once()
        mock_flash.assert_called_once_with("Deleted successfully", "success")
        mock_redirect.assert_called_once()

    def test_entity_name_configuration(self, controller_class, entity_name, audit_entity):
        """Test that entity_name is correctly configured"""
        controller = controller_class(repository=MagicMock())
        assert controller.entity_name == entity_name

    def test_audit_entity_configuration(self, controller_class, entity_name, audit_entity):
        """Test that audit_entity is correctly configured"""
        controller = controller_class(repository=MagicMock())
        assert controller.audit_entity == audit_entity