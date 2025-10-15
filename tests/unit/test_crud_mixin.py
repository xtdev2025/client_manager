"""
Unit tests for CrudControllerMixin.
"""
from unittest.mock import MagicMock, patch

import pytest

from app.controllers.crud_mixin import CrudControllerMixin
from app.repositories.base import CrudRepositoryProtocol
from app.schemas.forms import FormModel
from app.utils.crud import CrudOperationResult
from app.views.base_view import BaseView


class MockRepository(CrudRepositoryProtocol):
    """Mock repository for testing"""

    def __init__(self):
        self.items = [
            {"_id": "1", "name": "Item 1"},
            {"_id": "2", "name": "Item 2"},
        ]

    def get_all(self):
        return CrudOperationResult.ok(self.items)

    def get_by_id(self, entity_id: str):
        item = next((item for item in self.items if item["_id"] == entity_id), None)
        return CrudOperationResult.ok(item) if item else CrudOperationResult.fail("Not found")

    def create(self, data):
        new_item = {"_id": "3", **data}
        self.items.append(new_item)
        return CrudOperationResult.ok(new_item, message="Created successfully")

    def update(self, entity_id: str, data):
        item = next((item for item in self.items if item["_id"] == entity_id), None)
        if item:
            item.update(data)
            return CrudOperationResult.ok(item, message="Updated successfully")
        return CrudOperationResult.fail("Not found")

    def delete(self, entity_id: str):
        item = next((item for item in self.items if item["_id"] == entity_id), None)
        if item:
            self.items.remove(item)
            return CrudOperationResult.ok(None, message="Deleted successfully")
        return CrudOperationResult.fail("Not found")


class MockView(BaseView):
    """Mock view for testing"""

    def render_list(self, items):
        return f"Rendered list: {len(items)} items"

    def render_create_form(self, form_data=None, errors=None, **context):
        return f"Rendered create form: {form_data}, errors: {errors}"

    def render_edit_form(self, entity, form_data=None, errors=None, **context):
        return f"Rendered edit form for {entity['_id']}: {form_data}, errors: {errors}"


class MockSchema(FormModel):
    """Mock schema for testing"""

    name: str

    def to_payload(self):
        return {"name": self.name}

    def audit_payload(self):
        return {"name": self.name}


class TestCrudControllerMixin:
    """Test cases for CrudControllerMixin"""

    @pytest.fixture
    def mock_repo(self):
        """Create mock repository"""
        return MockRepository()

    @pytest.fixture
    def mock_view(self):
        """Create mock view"""
        return MockView()

    @pytest.fixture
    def mixin(self, mock_repo, mock_view):
        """Create CrudControllerMixin instance"""
        mixin = CrudControllerMixin(mock_repo)
        mixin.view = mock_view
        mixin.entity_name = "Test Item"
        mixin.audit_entity = "test_item"
        mixin.list_endpoint = "test.list"
        mixin.create_schema = MockSchema
        mixin.update_schema = MockSchema
        return mixin

    def test_init(self, mock_repo):
        """Test mixin initialization"""
        mixin = CrudControllerMixin(mock_repo)
        assert mixin.repository == mock_repo
        assert mixin._pending_audit_payload is None

    def test_list_view_success(self, mixin, mock_view):
        """Test successful list view"""
        with patch.object(mock_view, 'render_list') as mock_render:
            mock_render.return_value = "rendered list"
            result = mixin.list_view()
            assert result == "rendered list"
            mock_render.assert_called_once_with(mixin.get_list_items())

    def test_list_view_no_view_configured(self, mock_repo):
        """Test list view without view configured"""
        mixin = CrudControllerMixin(mock_repo)
        with pytest.raises(RuntimeError, match="View renderer not configured"):
            mixin.list_view()

    def test_create_view_get_request(self, mixin, mock_view):
        """Test create view GET request"""
        with patch('flask.request') as mock_request:
            mock_request.method = "GET"
            with patch.object(mixin, 'render_create_form') as mock_render:
                mock_render.return_value = "create form"
                result = mixin.create_view()
                assert result == "create form"

    def test_create_view_post_success(self, mixin):
        """Test create view POST request success"""
        with patch('app.controllers.crud_mixin.request') as mock_request:
            mock_request.method = "POST"
            mock_request.form.to_dict.return_value = {'name': 'New Item'}
            # Mock the parse_form to return valid schema
            with patch.object(mixin, '_parse_form') as mock_parse:
                mock_schema = MockSchema(name='New Item')
                mock_parse.return_value = (mock_schema, [])
                # Mock perform_create to return success
                with patch.object(mixin, 'perform_create') as mock_perform:
                    mock_result = CrudOperationResult.ok({"_id": "3", "name": "New Item"})  # Remove message
                    mock_perform.return_value = mock_result
                    with patch('app.controllers.crud_mixin.log_creation') as mock_log:
                        with patch('app.controllers.crud_mixin.flash') as mock_flash:
                            with patch('app.controllers.crud_mixin.redirect') as mock_redirect:
                                with patch('app.controllers.crud_mixin.url_for') as mock_url_for:
                                    mock_url_for.return_value = "/test/list"
                                    mock_redirect.return_value = "redirected"
                                    result = mixin.create_view()
                                    print(f"parse_form called: {mock_parse.called}")
                                    print(f"perform_create called: {mock_perform.called}")
                                    if mock_perform.called:
                                        assert result == "redirected"
                                        mock_flash.assert_called_with("Test Item created successfully", "success")
                                        mock_log.assert_called_once()
                                    else:
                                        assert False, "perform_create was not called"

    def test_create_view_post_validation_error(self, mixin):
        """Test create view POST request with validation error"""
        with patch('flask.request') as mock_request:
            mock_request.method = "POST"
            mock_request.form.to_dict.return_value = {'name': ''}  # Invalid data
            with patch.object(mixin, 'render_create_form') as mock_render:
                mock_render.return_value = "error form"
                result = mixin.create_view()
                assert result == "error form"

    def test_create_view_post_operation_failure(self, mixin, mock_repo):
        """Test create view POST request with operation failure"""
        # Make repository create fail
        original_create = mock_repo.create
        mock_repo.create = lambda data: CrudOperationResult.fail("Create failed", errors=["Error 1"])

        with patch('flask.request') as mock_request:
            mock_request.method = "POST"
            mock_request.form.to_dict.return_value = {'name': 'New Item'}
            with patch.object(mixin, 'render_create_form') as mock_render:
                mock_render.return_value = "error form"
                result = mixin.create_view()
                assert result == "error form"

        # Restore original method
        mock_repo.create = original_create

    def test_edit_view_get_success(self, mixin):
        """Test edit view GET request success"""
        with patch('flask.request') as mock_request:
            mock_request.method = "GET"
            with patch.object(mixin, 'render_edit_form') as mock_render:
                mock_render.return_value = "edit form"
                result = mixin.edit_view("1")
                assert result == "edit form"

    def test_edit_view_entity_not_found(self, mixin):
        """Test edit view with entity not found"""
        with patch('app.controllers.crud_mixin.flash') as mock_flash:
            with patch('app.controllers.crud_mixin.redirect') as mock_redirect:
                with patch('app.controllers.crud_mixin.url_for') as mock_url_for:
                    # Configure repository to return None for nonexistent entity
                    original_get_by_id = mixin.repository.get_by_id
                    mixin.repository.get_by_id = lambda entity_id: None if entity_id == "nonexistent" else original_get_by_id(entity_id)
                    mock_url_for.return_value = "/test/list"
                    mock_redirect.return_value = "redirected"
                    result = mixin.edit_view("nonexistent")
                    assert result == "redirected"
                    mock_flash.assert_called_with("Test Item not found", "danger")

    def test_edit_view_post_success(self, mixin):
        """Test edit view POST request success"""
        with patch('app.controllers.crud_mixin.request') as mock_request:
            mock_request.method = "POST"
            mock_request.form.to_dict.return_value = {'name': 'Updated Item'}
            # Mock the parse_form to return valid schema
            with patch.object(mixin, '_parse_form') as mock_parse:
                mock_schema = MockSchema(name='Updated Item')
                mock_parse.return_value = (mock_schema, [])
                # Mock perform_update to return success
                with patch.object(mixin, 'perform_update') as mock_perform:
                    mock_result = CrudOperationResult.ok({"_id": "1", "name": "Updated Item"})
                    mock_perform.return_value = mock_result
                    with patch('app.controllers.crud_mixin.log_update') as mock_log:
                        with patch('app.controllers.crud_mixin.flash') as mock_flash:
                            with patch('app.controllers.crud_mixin.redirect') as mock_redirect:
                                with patch('app.controllers.crud_mixin.url_for') as mock_url_for:
                                    mock_url_for.return_value = "/test/list"
                                    mock_redirect.return_value = "redirected"
                                    result = mixin.edit_view("1")
                                    assert result == "redirected"
                                    mock_flash.assert_called_with("Test Item updated successfully", "success")
                                    mock_log.assert_called_once()

    def test_delete_view_success(self, mixin):
        """Test delete view success"""
        with patch('app.controllers.crud_mixin.log_deletion') as mock_log:
            with patch('app.controllers.crud_mixin.flash') as mock_flash:
                with patch('app.controllers.crud_mixin.redirect') as mock_redirect:
                    with patch('app.controllers.crud_mixin.url_for') as mock_url_for:
                        # Mock repository.delete to return success
                        mock_result = CrudOperationResult.ok({"_id": "1"})
                        mixin.repository.delete = lambda entity_id: mock_result
                        mock_url_for.return_value = "/test/list"
                        mock_redirect.return_value = "redirected"
                        result = mixin.delete_view("1")
                        assert result == "redirected"
                        mock_flash.assert_called_with("Test Item deleted successfully", "success")
                        mock_log.assert_called_once()

    def test_delete_view_failure(self, mixin):
        """Test delete view failure"""
        with patch('app.controllers.crud_mixin.flash') as mock_flash:
            with patch('app.controllers.crud_mixin.redirect') as mock_redirect:
                with patch('app.controllers.crud_mixin.url_for') as mock_url_for:
                    # Mock repository.delete to return failure
                    mock_result = CrudOperationResult.fail("Not found")
                    mixin.repository.delete = lambda entity_id: mock_result
                    mock_url_for.return_value = "/test/list"
                    mock_redirect.return_value = "redirected"
                    result = mixin.delete_view("nonexistent")
                    assert result == "redirected"
                    mock_flash.assert_called_with("Not found", "danger")

    def test_redirect_to_list(self, mixin):
        """Test redirect to list"""
        with patch('app.controllers.crud_mixin.url_for') as mock_url_for:
            with patch('app.controllers.crud_mixin.redirect') as mock_redirect:
                mock_url_for.return_value = "/test/list"
                mock_redirect.return_value = "redirected"
                result = mixin.redirect_to_list()
                assert result == "redirected"
                mock_url_for.assert_called_with("test.list")

    def test_redirect_to_detail_with_endpoint(self, mixin):
        """Test redirect to detail with endpoint configured"""
        mixin.detail_endpoint = "test.detail"
        with patch('app.controllers.crud_mixin.url_for') as mock_url_for:
            with patch('app.controllers.crud_mixin.redirect') as mock_redirect:
                mock_url_for.return_value = "/detail/1"
                mock_redirect.return_value = "redirected"
                result = mixin.redirect_to_detail("1")
                assert result == "redirected"
                mock_url_for.assert_called_with("test.detail", entity_id="1")

    def test_redirect_to_detail_without_endpoint(self, mixin):
        """Test redirect to detail without endpoint configured"""
        with patch.object(mixin, 'redirect_to_list') as mock_redirect_list:
            mock_redirect_list.return_value = "redirected"
            result = mixin.redirect_to_detail("1")
            assert result == "redirected"

    def test_flash_errors(self, mixin):
        """Test flash errors"""
        with patch('app.controllers.crud_mixin.flash') as mock_flash:
            mixin.flash_errors(["Error 1", "Error 2"])
            assert mock_flash.call_count == 2
            mock_flash.assert_any_call("Error 1", "danger")
            mock_flash.assert_any_call("Error 2", "danger")

    def test_flash_errors_none(self, mixin):
        """Test flash errors with None"""
        # Should not raise error
        mixin.flash_errors(None)

    def test_set_audit_payload(self, mixin):
        """Test setting audit payload"""
        payload = {"key": "value"}
        mixin.set_audit_payload(payload)
        assert mixin._pending_audit_payload == payload

    def test_consume_audit_payload_pending(self, mixin):
        """Test consuming pending audit payload"""
        payload = {"key": "value"}
        mixin.set_audit_payload(payload)
        consumed = mixin._consume_audit_payload(None)
        assert consumed == payload
        assert mixin._pending_audit_payload is None

    def test_consume_audit_payload_from_schema(self, mixin):
        """Test consuming audit payload from schema"""
        schema = MockSchema(name="Test")
        consumed = mixin._consume_audit_payload(schema)
        assert consumed == {"name": "Test"}

    def test_consume_audit_payload_empty(self, mixin):
        """Test consuming empty audit payload"""
        consumed = mixin._consume_audit_payload(None)
        assert consumed == {}

    def test_resolve_entity_id_with_data(self):
        """Test resolving entity ID with data"""
        data = {"_id": "123"}
        result = CrudOperationResult.ok(data)
        entity_id = CrudControllerMixin._resolve_entity_id(result)
        assert entity_id == "123"

    def test_resolve_entity_id_without_data(self):
        """Test resolving entity ID without data"""
        result = CrudOperationResult.ok(None)
        entity_id = CrudControllerMixin._resolve_entity_id(result)
        assert entity_id is None

    def test_get_create_render_args(self, mixin):
        """Test get create render args"""
        args, kwargs = mixin.get_create_render_args(test="value")
        assert args == ()
        assert kwargs == {"test": "value"}

    def test_get_edit_render_args(self, mixin):
        """Test get edit render args"""
        entity = {"_id": "1", "name": "Test"}
        args, kwargs = mixin.get_edit_render_args(entity, test="value")
        assert args == (entity,)
        assert kwargs == {"test": "value"}

    def test_invoke_view(self, mixin, mock_view):
        """Test invoke view method"""
        # Add the method to the mock view
        mock_view.test_method = MagicMock(return_value="result")
        result = mixin._invoke_view("test_method", "arg1", kwarg1="value")
        assert result == "result"
        # Since the mock method doesn't have kwarg1 in signature, it should be filtered out
        mock_view.test_method.assert_called_with("arg1")

    def test_invoke_view_filters_kwargs(self, mixin, mock_view):
        """Test invoke view filters kwargs based on method signature"""
        # Add the method to the mock view
        mock_view.test_method = MagicMock(return_value="result")
        # Mock signature that only accepts 'arg1'
        mock_sig = MagicMock()
        mock_sig.parameters = {'arg1': MagicMock()}
        with patch('inspect.signature', return_value=mock_sig):
            result = mixin._invoke_view("test_method", "arg1", kwarg1="value", extra="ignored")
            assert result == "result"
            mock_view.test_method.assert_called_with("arg1")  # Only arg1 should be passed