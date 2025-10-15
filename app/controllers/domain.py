from bson import ObjectId
from flask import Blueprint, flash, redirect, url_for
from flask_login import login_required

from app import mongo
from app.controllers.auth import admin_required, super_admin_required
from app.controllers.crud_mixin import CrudControllerMixin
from app.models.domain import Domain
from app.repositories.base import ModelCrudRepository
from app.schemas.domain import DomainCreateSchema, DomainUpdateSchema
from app.views.domain_view import DomainView

domain = Blueprint("domain", __name__, url_prefix="/domains")


class DomainCrudController(CrudControllerMixin):
    entity_name = "Domain"
    audit_entity = "domain"
    list_endpoint = "domain.list_domains"
    detail_endpoint = "domain.view_domain"
    create_schema = DomainCreateSchema
    update_schema = DomainUpdateSchema
    view = DomainView

    def get_list_items(self):
        domains = super().get_list_items()
        enriched = []
        for entry in domains:
            if not entry:
                continue
            item = dict(entry)
            domain_id = item.get("_id")
            if domain_id:
                subdomain_count = Domain.get_subdomain_count(domain_id)
                item["subdomain_count"] = subdomain_count
                item["available_slots"] = item.get("domain_limit", 5) - subdomain_count
            enriched.append(item)
        return enriched


domain_crud = DomainCrudController(ModelCrudRepository(Domain))


@domain.route("/")
@login_required
@admin_required
def list_domains():
    """List all domains with subdomain counts"""
    return domain_crud.list_view()


@domain.route("/create", methods=["GET", "POST"])
@login_required
@super_admin_required
def create_domain():
    """Create a new domain"""
    return domain_crud.create_view()


@domain.route("/edit/<domain_id>", methods=["GET", "POST"])
@login_required
@super_admin_required
def edit_domain(domain_id):
    """Edit domain information"""
    return domain_crud.edit_view(domain_id)


@domain.route("/delete/<domain_id>", methods=["POST"])
@login_required
@super_admin_required
def delete_domain(domain_id):
    """Delete a domain"""
    return domain_crud.delete_view(domain_id)


@domain.route("/view/<domain_id>")
@login_required
@admin_required
def view_domain(domain_id):
    """View domain details"""
    domain_data = Domain.get_by_id(domain_id)
    if not domain_data:
        flash("Domain not found", "danger")
        return redirect(url_for("domain.list_domains"))

    # Get clients using this domain
    client_domains = list(mongo.db.client_domains.find({"domain_id": ObjectId(domain_id)}))

    # Enrich with client details
    for cd in client_domains:
        if "client_id" in cd:
            from app.models.client import Client

            client = Client.get_by_id(cd["client_id"])
            if client:
                cd["client"] = client

    return DomainView.render_view(domain_data, client_domains)
