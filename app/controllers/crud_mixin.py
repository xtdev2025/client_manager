from __future__ import annotations

from typing import Any, Dict, Optional, Tuple, Type

from inspect import signature
from flask import flash, redirect, request, url_for

from app.repositories.base import CrudRepositoryProtocol
from app.schemas.forms import FormModel, parse_form
from app.services.audit_helper import log_creation, log_deletion, log_update
from app.utils.crud import CrudOperationResult


class CrudControllerMixin:
    """Reusable helper encapsulating CRUD controller flows."""

    entity_name: str = "Item"
    audit_entity: str = "item"
    list_endpoint: str
    detail_endpoint: Optional[str] = None
    create_schema: Optional[Type[FormModel]] = None
    update_schema: Optional[Type[FormModel]] = None
    view = None

    success_category: str = "success"
    error_category: str = "danger"

    def __init__(self, repository: CrudRepositoryProtocol):
        self.repository = repository
        self._pending_audit_payload: Optional[Dict[str, Any]] = None

    # --- list ---
    def list_view(self):
        items = self.get_list_items()
        return self.render_list(items)

    def get_list_items(self):
        return self.repository.get_all()

    def render_list(self, items):
        if not self.view:
            raise RuntimeError("View renderer not configured for list view")
        return self.view.render_list(items)

    # --- create ---
    def create_view(self, **route_kwargs):
        def render_with_context(form_data=None, errors=None):
            context = self.get_create_context(**route_kwargs)
            return self.render_create_form(
                form_data=form_data,
                errors=errors,
                **context,
            )

        if request.method == "POST":
            schema, errors = self._parse_form(self.create_schema)
            if errors:
                self.flash_errors(errors)
                return render_with_context(form_data=request.form.to_dict(), errors=errors)

            result = self.perform_create(schema, **route_kwargs)
            return self._handle_operation_result(
                result,
                success_message=self.create_success_message(result),
                failure_context={"form_data": request.form.to_dict(), "errors": result.errors},
                render_callback=lambda fd, errs: render_with_context(form_data=fd, errors=errs),
                audit_callback=lambda entity_id: log_creation(
                    self.audit_entity,
                    entity_id,
                    self._consume_audit_payload(schema),
                ),
                redirect_callback=lambda entity_id: self.after_create_redirect(
                    entity_id, result, **route_kwargs
                ),
            )

        return render_with_context()

    def get_create_context(self, **route_kwargs) -> Dict[str, Any]:
        return {}

    def render_create_form(self, form_data=None, errors=None, **context):
        if not self.view or not hasattr(self.view, "render_create_form"):
            raise RuntimeError("View renderer not configured for create form")
        args, kwargs = self.get_create_render_args(**context)
        kwargs = dict(kwargs)
        kwargs.update({"form_data": form_data, "errors": errors})
        return self._invoke_view("render_create_form", *args, **kwargs)

    def perform_create(self, schema: Optional[FormModel], **route_kwargs) -> CrudOperationResult:
        payload = schema.to_payload() if schema else request.form.to_dict()
        return self.repository.create(payload)

    def create_success_message(self, result: CrudOperationResult) -> str:
        return result.message or f"{self.entity_name} created successfully"

    def after_create_redirect(
        self, entity_id: Optional[str], result: CrudOperationResult, **route_kwargs
    ):
        return self.redirect_to_list()

    # --- edit ---
    def edit_view(self, entity_id: str):
        entity = self.repository.get_by_id(entity_id)
        if not entity:
            flash(f"{self.entity_name} not found", self.error_category)
            return self.redirect_to_list()

        context = self.get_edit_context(entity)

        if request.method == "POST":
            schema, errors = self._parse_form(self.update_schema)
            if errors:
                self.flash_errors(errors)
                return self.render_edit_form(
                    entity,
                    form_data=request.form.to_dict(),
                    errors=errors,
                    **context,
                )

            result = self.perform_update(entity_id, schema)
            return self._handle_operation_result(
                result,
                success_message=self.update_success_message(result),
                failure_context={"form_data": request.form.to_dict(), "errors": result.errors},
                render_callback=lambda fd, errs: self.render_edit_form(
                    entity, form_data=fd, errors=errs, **context
                ),
                audit_callback=lambda _: log_update(
                    self.audit_entity,
                    entity_id,
                    self._consume_audit_payload(schema),
                ),
                redirect_callback=lambda _: self.after_update_redirect(entity_id, result),
            )

        return self.render_edit_form(entity, **context)

    def get_edit_context(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        return {}

    def render_edit_form(self, entity, form_data=None, errors=None, **context):
        if not self.view or not hasattr(self.view, "render_edit_form"):
            raise RuntimeError("View renderer not configured for edit form")
        args, kwargs = self.get_edit_render_args(entity, **context)
        kwargs = dict(kwargs)
        kwargs.update({"form_data": form_data, "errors": errors})
        return self._invoke_view("render_edit_form", *args, **kwargs)

    def perform_update(self, entity_id: str, schema: Optional[FormModel]) -> CrudOperationResult:
        payload = schema.to_payload() if schema else request.form.to_dict()
        return self.repository.update(entity_id, payload)

    def update_success_message(self, result: CrudOperationResult) -> str:
        return result.message or f"{self.entity_name} updated successfully"

    def after_update_redirect(self, entity_id: str, result: CrudOperationResult):
        return self.redirect_to_list()

    # --- delete ---
    def delete_view(self, entity_id: str):
        entity = self.repository.get_by_id(entity_id)
        audit_payload = self._consume_audit_payload(None)
        result = self.perform_delete(entity_id)

        message = result.message or (
            f"{self.entity_name} deleted successfully" if result.success else f"Unable to delete {self.entity_name.lower()}"
        )
        flash(message, self.success_category if result.success else self.error_category)

        if result.success:
            payload = audit_payload if audit_payload is not None else (entity or {})
            log_deletion(self.audit_entity, entity_id, payload=payload)

        return self.after_delete_redirect(entity_id, result)

    def perform_delete(self, entity_id: str) -> CrudOperationResult:
        return self.repository.delete(entity_id)

    def after_delete_redirect(self, entity_id: str, result: CrudOperationResult):
        return self.redirect_to_list()

    # --- helpers ---
    def redirect_to_list(self):
        return redirect(url_for(self.list_endpoint))

    def redirect_to_detail(self, entity_id: str):
        if not self.detail_endpoint:
            return self.redirect_to_list()
        return redirect(url_for(self.detail_endpoint, entity_id=entity_id))

    def flash_errors(self, errors: Optional[list[str]]):
        if not errors:
            return
        for error in errors:
            flash(error, self.error_category)

    def _parse_form(self, schema_cls: Optional[Type[FormModel]]):
        if not schema_cls:
            return None, []
        return parse_form(schema_cls, request.form)

    def _handle_operation_result(
        self,
        result: CrudOperationResult,
        success_message: str,
        failure_context: Dict[str, Any],
        render_callback,
        audit_callback,
        redirect_callback,
    ):
        if result.success:
            flash(success_message, self.success_category)
            entity_id = self._resolve_entity_id(result)
            audit_callback(entity_id)
            return redirect_callback(entity_id)

        errors = result.errors or ([] if not result.message else [result.message])
        self.flash_errors(errors)
        return render_callback(failure_context.get("form_data"), errors)

    @staticmethod
    def _resolve_entity_id(result: CrudOperationResult) -> Optional[str]:
        if result.data and "_id" in result.data:
            return str(result.data["_id"])
        return None

    def get_create_render_args(self, **context) -> Tuple[Tuple[Any, ...], Dict[str, Any]]:
        return (), context

    def get_edit_render_args(
        self, entity: Dict[str, Any], **context
    ) -> Tuple[Tuple[Any, ...], Dict[str, Any]]:
        return (entity,), context

    def _invoke_view(self, method_name: str, *args, **kwargs):
        method = getattr(self.view, method_name)
        sig = signature(method)
        filtered_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}
        return method(*args, **filtered_kwargs)

    def set_audit_payload(self, payload: Dict[str, Any]) -> None:
        self._pending_audit_payload = payload

    def _consume_audit_payload(self, schema: Optional[FormModel]) -> Dict[str, Any]:
        if self._pending_audit_payload is not None:
            payload = self._pending_audit_payload
            self._pending_audit_payload = None
            return payload
        if schema:
            return schema.audit_payload()
        return {}
