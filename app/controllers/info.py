from flask import Blueprint, flash, redirect, url_for
from flask_login import current_user, login_required

from app.controllers.auth import admin_required
from app.controllers.crud_mixin import CrudControllerMixin
from app.models.client import Client
from app.models.domain import Domain
from app.models.info import Info
from app.models.template import Template
from app.repositories.base import ModelCrudRepository
from app.schemas.crud import InfoCreateSchema, InfoUpdateSchema
from app.views.info_view import InfoView
from app.utils.crud import CrudOperationResult

info = Blueprint("info", __name__, url_prefix="/infos")


class InfoCrudController(CrudControllerMixin):
    entity_name = "Information"
    audit_entity = "info"
    list_endpoint = "info.list_infos"
    detail_endpoint = "info.view_info"
    create_schema = InfoCreateSchema
    update_schema = InfoUpdateSchema
    view = InfoView

    def __init__(self, repository: ModelCrudRepository):
        super().__init__(repository)
        self._delete_entity_cache = None

    def get_create_context(self, client=None, client_id=None, **route_kwargs):
        client_data = client or (Client.get_by_id(client_id) if client_id else None)
        templates = Template.get_all()
        domains = Domain.get_client_domains(str(client_data["_id"])) if client_data else []
        return {
            "client": client_data,
            "templates": templates,
            "domains": domains,
        }

    def get_list_items(self):
        infos = super().get_list_items()
        for info_data in infos:
            if not info_data:
                continue
            client_id = info_data.get("client_id")
            if client_id:
                client = Client.get_by_id(client_id)
                if client:
                    info_data["client"] = client
        return infos

    def get_edit_context(self, entity: dict) -> dict:
        client = Client.get_by_id(entity.get("client_id")) if entity else None
        templates = Template.get_all()
        domains = Domain.get_client_domains(str(entity.get("client_id"))) if entity else []
        return {
            "client": client,
            "templates": templates,
            "domains": domains,
        }

    def get_create_render_args(self, **context):
        client = context.get("client")
        templates = context.get("templates", [])
        domains = context.get("domains", [])
        return (client, templates, domains), {}

    def get_edit_render_args(self, entity: dict, **context):
        client = context.get("client")
        templates = context.get("templates", [])
        domains = context.get("domains", [])
        return (client, entity, templates, domains), {}

    def perform_create(
        self, schema: InfoCreateSchema | None, client=None, client_id=None, **route_kwargs
    ) -> CrudOperationResult:
        target_client_id = client_id or (str(client["_id"]) if client else None)
        payload = schema.to_payload() if schema else {}
        payload["client_id"] = target_client_id
        self.set_audit_payload({
            "client_id": target_client_id,
            "agencia": payload.get("agencia"),
            "conta": payload.get("conta"),
            "status": payload.get("status"),
        })
        return self.repository.create(payload)

    def perform_update(self, entity_id: str, schema: InfoUpdateSchema | None) -> CrudOperationResult:
        payload = schema.to_payload() if schema else {}
        self.set_audit_payload({
            "agencia": payload.get("agencia"),
            "conta": payload.get("conta"),
            "status": payload.get("status"),
        })
        return self.repository.update(entity_id, payload)

    def after_create_redirect(self, entity_id: str | None, result, client=None, client_id=None, **route_kwargs):
        destination = client_id or (str(client["_id"]) if client else None)
        if destination:
            return redirect(url_for("info.list_client_infos", client_id=destination))
        return self.redirect_to_list()

    def after_update_redirect(self, entity_id: str, result):
        return redirect(url_for("info.view_info", info_id=entity_id))

    def delete_view(self, entity_id: str):
        self._delete_entity_cache = self.repository.get_by_id(entity_id)
        if self._delete_entity_cache:
            sanitized = {
                "client_id": str(self._delete_entity_cache.get("client_id"))
                if self._delete_entity_cache.get("client_id")
                else None,
                "agencia": self._delete_entity_cache.get("agencia"),
                "conta": self._delete_entity_cache.get("conta"),
                "status": self._delete_entity_cache.get("status"),
            }
            self.set_audit_payload(sanitized)
        return super().delete_view(entity_id)

    def after_delete_redirect(self, entity_id: str, result):
        client_id = None
        if self._delete_entity_cache and "client_id" in self._delete_entity_cache:
            client_id = str(self._delete_entity_cache["client_id"])
        self._delete_entity_cache = None
        if client_id:
            return redirect(url_for("info.list_client_infos", client_id=client_id))
        return self.redirect_to_list()


info_crud = InfoCrudController(ModelCrudRepository(Info))


def client_or_admin_required(func):
    """Decorator to ensure user is either the client or an admin"""

    @login_required
    def client_or_admin_wrapper(*args, **kwargs):
        # If user is admin, allow access
        if current_user.is_admin:
            return func(*args, **kwargs)

        # If we're looking at a specific info, check if user owns it
        if "info_id" in kwargs:
            info_data = Info.get_by_id(kwargs["info_id"])
            if not info_data:
                flash("Information not found", "danger")
                return redirect(url_for("main.dashboard"))

            # If user is the client that owns this info, allow access
            if current_user.user and str(info_data["client_id"]) == str(current_user.user["_id"]):
                return func(*args, **kwargs)

        # If we're looking at all infos for a client
        if "client_id" in kwargs:
            # If user is the client, allow access to their own infos
            if current_user.user and str(kwargs["client_id"]) == str(current_user.user["_id"]):
                return func(*args, **kwargs)

        # Otherwise deny access
        flash("You do not have permission to access this resource", "danger")
        return redirect(url_for("main.dashboard"))

    # Copy func attributes to the wrapper function
    client_or_admin_wrapper.__name__ = func.__name__
    client_or_admin_wrapper.__doc__ = func.__doc__
    client_or_admin_wrapper.__module__ = func.__module__

    return client_or_admin_wrapper


@info.route("/")
@login_required
@admin_required
def list_infos():
    """List all infos (admin only)"""
    return info_crud.list_view()


@info.route("/client/<client_id>")
@login_required
@client_or_admin_required
def list_client_infos(client_id):
    """List all infos for a specific client"""
    client = Client.get_by_id(client_id)
    if not client:
        flash("Client not found", "danger")
        return redirect(url_for("main.dashboard"))

    infos = Info.get_by_client(client_id)

    return InfoView.render_client_list(client, infos)


@info.route("/create/<client_id>", methods=["GET", "POST"])
@login_required
@client_or_admin_required
def create_info(client_id):
    """Create a new info entry for a client"""
    client = Client.get_by_id(client_id)
    if not client:
        flash("Client not found", "danger")
        return redirect(url_for("main.dashboard"))

    return info_crud.create_view(client=client, client_id=client_id)


@info.route("/edit/<info_id>", methods=["GET", "POST"])
@login_required
@client_or_admin_required
def edit_info(info_id):
    """Edit info"""
    return info_crud.edit_view(info_id)


@info.route("/view/<info_id>")
@login_required
@client_or_admin_required
def view_info(info_id):
    """View info details"""
    info_data = Info.get_with_relations(info_id)
    if not info_data:
        flash("Information not found", "danger")
        return redirect(url_for("main.dashboard"))

    return InfoView.render_view(info_data)


@info.route("/delete/<info_id>", methods=["POST"])
@login_required
@client_or_admin_required
def delete_info(info_id):
    """Delete info"""
    return info_crud.delete_view(info_id)
