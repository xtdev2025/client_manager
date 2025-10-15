import random
import string

from bson import ObjectId
from flask import Blueprint, flash, redirect, request, url_for
from flask_login import current_user, login_required

from app import mongo
from app.controllers.auth import admin_required, super_admin_required
from app.controllers.crud_mixin import CrudControllerMixin
from app.models.client import Client
from app.models.client_crypto_payout import ClientCryptoPayout
from app.models.domain import Domain
from app.models.plan import Plan
from app.models.template import Template
from app.repositories.base import ModelCrudRepository
from app.schemas.client import ClientCreateSchema, ClientUpdateSchema
from app.schemas.forms import parse_form
from app.services.audit_helper import log_creation, log_update
from app.services.payout_orchestration_service import PayoutOrchestrationService
from app.views.client_view import ClientView
from app.utils.crud import CrudOperationResult

client = Blueprint("client", __name__, url_prefix="/clients")


class ClientCrudController(CrudControllerMixin):
    entity_name = "Client"
    audit_entity = "client"
    list_endpoint = "client.list_clients"
    detail_endpoint = "client.view_client"
    create_schema = ClientCreateSchema
    update_schema = ClientUpdateSchema
    view = ClientView

    def get_create_context(self, **route_kwargs):
        plans = Plan.get_all()
        templates = Template.get_all()
        domains = Domain.get_all()
        enriched_domains = []
        for domain in domains:
            if not domain:
                continue
            domain_copy = dict(domain)
            domain_id = domain_copy.get("_id")
            if domain_id:
                subdomain_count = Domain.get_subdomain_count(domain_id)
                domain_copy["subdomain_count"] = subdomain_count
            enriched_domains.append(domain_copy)
        return {
            "plans": plans,
            "templates": templates,
            "domains": enriched_domains,
        }

    def get_create_render_args(self, **context):
        plans = context.get("plans", [])
        templates = context.get("templates", [])
        domains = context.get("domains", [])
        return (plans,), {"templates": templates, "domains": domains}

    def perform_create(self, schema: ClientCreateSchema | None, **route_kwargs) -> CrudOperationResult:
        if not schema:
            return CrudOperationResult.fail("Invalid data")

        payload = schema.to_payload()

        username = payload.get("username")
        password = payload.get("password")
        plan_id = payload.get("plan_id")
        template_id = payload.get("template_id")
        domain_id = payload.get("domain_id")
        status = payload.get("status", "active")
        plan_activation_date = payload.get("plan_activation_date")
        plan_expiration_date = payload.get("plan_expiration_date")
        requested_domain = payload.get("domain")

        success, response = Client.create(
            username,
            password,
            plan_id,
            template_id,
            status,
            plan_activation_date=plan_activation_date,
            plan_expiration_date=plan_expiration_date,
        )

        if not success:
            return CrudOperationResult.fail(response)

        client_id = response
        assigned_domain = None

        if domain_id and requested_domain and template_id:
            selected_domain = Domain.get_by_id(domain_id)
            if selected_domain:
                domain_name = selected_domain.get("name", "seusite.com")
                unique_subdomain = generate_unique_subdomain(domain_id, requested_domain)

                if not unique_subdomain:
                    flash("Client created but failed to generate unique subdomain", "warning")
                else:
                    current_count = mongo.db.client_domains.count_documents(
                        {"domain_id": ObjectId(domain_id)}
                    )
                    domain_limit = selected_domain.get("domain_limit", 5)

                    if current_count >= domain_limit:
                        flash(
                            f"Client created but domain has reached its limit ({domain_limit} subdomains)",
                            "warning",
                        )
                    else:
                        domain_success, domain_message = Domain.assign_to_client(
                            client_id=client_id,
                            domain_id=domain_id,
                            subdomain=unique_subdomain,
                        )
                        if domain_success:
                            assigned_domain = f"{unique_subdomain}.{domain_name}"
                            if unique_subdomain != requested_domain:
                                flash(
                                    f"Client created with domain {assigned_domain} ('{requested_domain}' já estava em uso)",
                                    "success",
                                )
                            else:
                                flash(
                                    f"Client created with domain {assigned_domain}",
                                    "success",
                                )
                        else:
                            flash(
                                f"Client created but domain assignment failed: {domain_message}",
                                "warning",
                            )
            else:
                flash("Client created but selected domain not found", "warning")
        created_client = Client.get_by_id(client_id)
        self.set_audit_payload(
            {
                "username": username,
                "plan_id": plan_id,
                "template_id": template_id,
                "status": status,
                "assigned_domain": assigned_domain,
            }
        )

        return CrudOperationResult.ok(data=created_client, message="Client created successfully")

    def delete_view(self, entity_id: str):
        entity = self.repository.get_by_id(entity_id)
        if entity:
            sanitized = {
                "username": entity.get("username"),
                "plan_id": str(entity.get("plan_id")) if entity.get("plan_id") else None,
                "template_id": str(entity.get("template_id")) if entity.get("template_id") else None,
                "status": entity.get("status"),
            }
            self.set_audit_payload(sanitized)
        return super().delete_view(entity_id)


client_crud = ClientCrudController(ModelCrudRepository(Client))


def generate_unique_subdomain(domain_id, base_subdomain="", max_attempts=10):
    """
    Generate a unique subdomain for a given domain.

    Args:
        domain_id: The domain ID to check against
        base_subdomain: Base name to use (optional)
        max_attempts: Maximum number of attempts to generate unique subdomain

    Returns:
        Unique subdomain string or None if failed
    """
    for attempt in range(max_attempts):
        if attempt == 0 and base_subdomain:
            # First try: use the base subdomain as-is
            subdomain = base_subdomain.lower().strip()
        elif base_subdomain:
            # Subsequent tries: append random suffix
            suffix = "".join(random.choices(string.digits, k=3))
            subdomain = f"{base_subdomain}{suffix}"
        else:
            # No base provided: generate completely random
            subdomain = "".join(random.choices(string.ascii_lowercase, k=6)) + "".join(
                random.choices(string.digits, k=3)
            )

        # Sanitize subdomain (only alphanumeric and hyphens)
        subdomain = "".join(c for c in subdomain if c.isalnum() or c == "-")

        # Check if subdomain already exists
        existing = mongo.db.client_domains.find_one(
            {"domain_id": ObjectId(domain_id), "subdomain": subdomain}
        )

        if not existing:
            return subdomain

    return None


@client.route("/")
@login_required
@admin_required
def list_clients():
    """List all clients"""
    return client_crud.list_view()


@client.route("/create", methods=["GET", "POST"])
@login_required
@admin_required
def create_client():
    """Create a new client"""
    return client_crud.create_view()


@client.route("/edit/<client_id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_client(client_id):
    """Edit client information - redirect to unified management page"""
    return redirect(url_for("client.view_client", client_id=client_id))


@client.route("/delete/<client_id>", methods=["POST"])
@login_required
@admin_required
def delete_client(client_id):
    """Delete a client"""
    if request.method == "POST":
        return client_crud.delete_view(client_id)
    return redirect(url_for("client.list_clients"))


@client.route("/view/<client_id>", methods=["GET", "POST"])
@login_required
@admin_required
def view_client(client_id):
    """View and manage client details (unified view/edit/domains page)"""
    client_data = Client.get_by_id(client_id)
    if not client_data:
        flash("Client not found", "danger")
        return redirect(url_for("client.list_clients"))

    plans = Plan.get_all()
    templates = Template.get_all()

    # Get client domains
    client_domains = Domain.get_client_domains(client_id)

    # Get all available domains for assignment
    available_domains = Domain.get_all()

    # Enrich domains with subdomain counts
    enriched_domains = []
    for domain in available_domains:
        domain_id = domain["_id"]
        subdomain_count = mongo.db.client_domains.count_documents({"domain_id": domain_id})
        domain["subdomain_count"] = subdomain_count
        enriched_domains.append(domain)

    # Get domain limit (using the first domain's limit as default)
    domain_limit = 5  # Default
    if available_domains:
        domain_limit = available_domains[0].get("domain_limit", 5)

    # Prepare payout context
    payout_documents = ClientCryptoPayout.get_by_client(client_id, days=180)
    client_payouts = []
    for payout in payout_documents:
        payout_entry = payout.copy()
        payout_entry["payout_id"] = str(payout.get("_id"))
        client_payouts.append(payout_entry)

    payout_status_summary = {}
    for payout in payout_documents:
        status_key = payout.get("status", ClientCryptoPayout.STATUS_PENDING)
        payout_status_summary[status_key] = payout_status_summary.get(status_key, 0) + 1

    wallet_prefill = dict(client_data.get("crypto_wallet_preferences") or {})
    if not wallet_prefill and client_payouts:
        last_payout = client_payouts[0]
        wallet_prefill = {
            "asset": last_payout.get("asset"),
            "network": last_payout.get("network"),
            "wallet_address": last_payout.get("wallet_address"),
            "memo_tag": last_payout.get("memo_tag"),
            "default_amount": last_payout.get("amount"),
        }

    plan_lookup = {str(plan["_id"]): plan for plan in plans}
    plan_document = None
    if client_data.get("plan_id"):
        plan_document = plan_lookup.get(str(client_data["plan_id"])) or Plan.get_by_id(
            client_data["plan_id"]
        )

    suggested_amount = wallet_prefill.get("default_amount") if wallet_prefill else None
    if suggested_amount is None and plan_document and plan_document.get("price"):
        try:
            suggested_amount = float(plan_document.get("price"))
        except (TypeError, ValueError):
            suggested_amount = None

    # Handle POST request (edit form submission)
    if request.method == "POST":
        schema, errors = parse_form(ClientUpdateSchema, request.form)
        if errors:
            for error in errors:
                flash(error, "danger")
            return ClientView.render_manage(
                client_data,
                plans,
                templates,
                client_domains,
                enriched_domains,
                domain_limit,
                client_payouts,
                wallet_prefill,
                payout_status_summary,
                suggested_amount,
                form_data=request.form.to_dict(),
            )

        update_payload = schema.to_payload()

        success, message = Client.update(client_id, update_payload)

        if success:
            log_update(
                "client",
                client_id,
                {
                    "username": update_payload.get("username", client_data.get("username")),
                    "plan_id": update_payload.get("plan_id"),
                    "status": update_payload.get("status"),
                    "password_changed": "password" in update_payload,
                },
            )
            flash("Client updated successfully", "success")
            return redirect(url_for("client.view_client", client_id=client_id))

        flash(f"Error updating client: {message}", "danger")
        return ClientView.render_manage(
            client_data,
            plans,
            templates,
            client_domains,
            enriched_domains,
            domain_limit,
            client_payouts,
            wallet_prefill,
            payout_status_summary,
            suggested_amount,
            form_data=request.form.to_dict(),
        )

    # GET request - render the unified management page
    return ClientView.render_manage(
        client_data,
        plans,
        templates,
        client_domains,
        enriched_domains,
        domain_limit,
        client_payouts,
        wallet_prefill,
        payout_status_summary,
        suggested_amount,
    )


@client.route("/<client_id>/payouts/initiate", methods=["POST"])
@login_required
@admin_required
def initiate_payout(client_id):
    """Trigger a Heleket payout for a client from the admin workflow."""
    redirect_url = url_for("client.view_client", client_id=client_id) + "#payouts"

    client_data = Client.get_by_id(client_id)
    if not client_data:
        flash("Client not found", "danger")
        return redirect(url_for("client.list_clients"))

    asset = (request.form.get("asset") or "").strip().upper()
    network = (request.form.get("network") or "").strip().upper()
    amount_input = (request.form.get("amount") or "").strip()
    wallet_address = (request.form.get("wallet_address") or "").strip()
    memo_tag = (request.form.get("memo_tag") or "").strip() or None

    if not asset or not network or not amount_input or not wallet_address:
        flash("Preencha todos os campos obrigatórios do payout", "danger")
        return redirect(redirect_url)

    try:
        amount_value = float(amount_input)
    except (TypeError, ValueError):
        flash("Valor do payout inválido", "danger")
        return redirect(redirect_url)

    metadata = {
        "initiated_by": getattr(current_user, "username", str(current_user.id)),
        "source": "admin_dashboard",
    }

    trigger_metadata = {
        "form": "client_manage",
        "requested_path": request.referrer,
    }

    success, payload, error_message = PayoutOrchestrationService.initiate_payout(
        client_id=client_id,
        asset=asset,
        network=network,
        amount=amount_value,
        wallet_address=wallet_address,
        memo_tag=memo_tag,
        created_by=current_user.id,
        metadata=metadata,
        trigger_metadata=trigger_metadata,
    )

    if not success:
        flash(error_message or "Não foi possível iniciar o payout.", "danger")
        return redirect(redirect_url)

    payout_id = payload.get("payout_id") if payload else None
    status = payload.get("status") if payload else None

    log_creation(
        "payout",
        entity_id=payout_id,
        payload={
            "client_id": str(client_id),
            "asset": asset,
            "network": network,
            "amount": amount_value,
            "status": status,
            "memo_tag": memo_tag,
        },
    )

    remember_wallet = request.form.get("remember_wallet") == "on"
    wallet_saved = False
    if remember_wallet:
        wallet_saved = Client.update_crypto_wallet_preferences(
            client_id,
            {
                "asset": asset,
                "network": network,
                "wallet_address": wallet_address,
                "memo_tag": memo_tag,
                "default_amount": amount_value,
            },
        )

    success_message = "Payout registrado e enviado."
    if status:
        success_message = f"Payout iniciado com status {status}."
    if wallet_saved:
        success_message += " Preferências de carteira salvas."

    flash(success_message, "success")
    return redirect(redirect_url)


@client.route("/<client_id>/domains")
@login_required
@admin_required
def manage_domains(client_id):
    """Manage domains for a client - redirect to unified management page"""
    return redirect(url_for("client.view_client", client_id=client_id))


@client.route("/<client_id>/domains/add", methods=["POST"])
@login_required
@super_admin_required
def add_domain(client_id):
    """Add a domain to a client"""
    if request.method == "POST":
        domain_id = request.form.get("domain_id")
        subdomain = request.form.get("subdomain")

        if not domain_id or not subdomain:
            flash("Please provide both domain and subdomain", "danger")
            return redirect(url_for("client.manage_domains", client_id=client_id))

        # Assign domain to client
        success, message = Domain.assign_to_client(client_id, domain_id, subdomain)

        if success:
            flash("Domain assigned successfully", "success")
        else:
            flash(f"Error assigning domain: {message}", "danger")

    return redirect(url_for("client.manage_domains", client_id=client_id))


@client.route("/<client_id>/domains/remove/<client_domain_id>", methods=["POST"])
@login_required
@super_admin_required
def remove_domain(client_id, client_domain_id):
    """Remove a domain from a client"""
    if request.method == "POST":
        # Remove domain from client
        success, message = Domain.remove_from_client(client_id, client_domain_id)

        if success:
            flash("Domain removed successfully", "success")
        else:
            flash(f"Error removing domain: {message}", "danger")

    return redirect(url_for("client.manage_domains", client_id=client_id))
