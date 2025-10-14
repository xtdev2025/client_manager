import random
import string

from bson import ObjectId
from flask import Blueprint, abort, flash, redirect, request, url_for
from flask_login import current_user, login_required

from app import mongo
from app.controllers.auth import admin_required, super_admin_required
from app.models.client import Client
from app.models.client_crypto_payout import ClientCryptoPayout
from app.models.domain import Domain
from app.models.plan import Plan
from app.models.template import Template
from app.models.user import User
from app.services.audit_service import AuditService
from app.services.payout_orchestration_service import PayoutOrchestrationService
from app.views.client_view import ClientView

client = Blueprint("client", __name__, url_prefix="/clients")


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
    clients = Client.get_all()

    # ClientView handles enriching client data with plan information
    return ClientView.render_list(clients)


@client.route("/create", methods=["GET", "POST"])
@login_required
@admin_required
def create_client():
    """Create a new client"""
    plans = Plan.get_all()
    templates = Template.get_all()
    domains = Domain.get_all()  # Get all available domains

    # Enrich domains with subdomain counts
    enriched_domains = []
    for domain in domains:
        domain_id = domain["_id"]
        subdomain_count = mongo.db.client_domains.count_documents({"domain_id": domain_id})
        domain["subdomain_count"] = subdomain_count
        enriched_domains.append(domain)

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        plan_id = request.form.get("plan_id") or None
        template_id = request.form.get("template_id") or None
        domain_id = request.form.get("domain_id") or None  # Selected domain ID
        status = request.form.get("status", "active")
        plan_activation_date = request.form.get("plan_activation_date") or None
        plan_expiration_date = request.form.get("plan_expiration_date") or None
        domain = request.form.get("domain", "").strip()  # Subdomain

        form_payload = {
            "username": username,
            "plan_id": plan_id,
            "template_id": template_id,
            "domain_id": domain_id,
            "status": status,
            "plan_activation_date": plan_activation_date,
            "plan_expiration_date": plan_expiration_date,
            "domain": domain,
        }

        if not username or not password:
            flash("Please provide username and password", "danger")
            return ClientView.render_create_form(
                plans, templates, enriched_domains, form_data=form_payload
            )

        # Create client
        success, message = Client.create(
            username,
            password,
            plan_id,
            template_id,
            status,
            plan_activation_date=plan_activation_date,
            plan_expiration_date=plan_expiration_date,
        )

        if success:
            client_id = message  # message contains the client_id on success

            # Create domain association if domain_id, subdomain and template are provided
            if domain_id and domain and template_id:
                # Get the selected domain
                selected_domain = Domain.get_by_id(domain_id)

                if selected_domain:
                    domain_name = selected_domain.get("name", "seusite.com")

                    # Generate unique subdomain (try user input first, then add random suffix if needed)
                    unique_subdomain = generate_unique_subdomain(domain_id, domain)

                    if not unique_subdomain:
                        flash("Client created but failed to generate unique subdomain", "warning")
                    else:
                        # Check if domain has reached its limit
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
                            # Assign subdomain to client
                            domain_success, domain_message = Domain.assign_to_client(
                                client_id=client_id, domain_id=domain_id, subdomain=unique_subdomain
                            )

                            if domain_success:
                                actual_domain = f"{unique_subdomain}.{domain_name}"
                                if unique_subdomain != domain:
                                    flash(
                                        f"Client created with domain {actual_domain} ('{domain}' já estava em uso)",
                                        "success",
                                    )
                                else:
                                    flash(f"Client created with domain {actual_domain}", "success")
                            else:
                                flash(
                                    f"Client created but domain assignment failed: {domain_message}",
                                    "warning",
                                )
                else:
                    flash("Client created but selected domain not found", "warning")
            else:
                flash("Client created successfully", "success")

            # Log client creation in audit trail
            AuditService.log_client_action(
                "create",
                client_id,
                {
                    "username": username,
                    "plan_id": plan_id,
                    "template_id": template_id,
                    "status": status,
                    "domain": f"{domain}.seusite.com" if domain and template_id else None,
                },
            )

            return redirect(url_for("client.list_clients"))
        else:
            flash(f"Error creating client: {message}", "danger")
            return ClientView.render_create_form(
                plans, templates, enriched_domains, form_data=form_payload
            )

    return ClientView.render_create_form(plans, templates, enriched_domains)


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
        # Get client data before deletion for audit log
        client_data = Client.get_by_id(client_id)
        username = client_data.get("username", "unknown") if client_data else "unknown"

        success, message = Client.delete(client_id)

        if success:
            # Log client deletion in audit trail
            AuditService.log_client_action("delete", client_id, {"username": username})
            flash("Client deleted successfully", "success")
        else:
            flash(f"Error deleting client: {message}", "danger")

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
        plan_activation_date = request.form.get("plan_activation_date") or None
        plan_expiration_date = request.form.get("plan_expiration_date") or None

        plan_id_value = request.form.get("plan_id") or None
        template_id_value = request.form.get("template_id") or None

        data = {
            "username": request.form.get("username"),
            "plan_id": plan_id_value,
            "template_id": template_id_value,
            "status": request.form.get("status"),
            "plan_activation_date": plan_activation_date,
            "plan_expiration_date": plan_expiration_date,
        }

        # Only update password if provided
        if request.form.get("password"):
            data["password"] = request.form.get("password")

        # Update client
        success, message = Client.update(client_id, data)

        if success:
            # Log client update in audit trail
            AuditService.log_client_action(
                "update",
                client_id,
                {
                    "username": data.get("username"),
                    "plan_id": plan_id_value,
                    "status": data.get("status"),
                    "password_changed": "password" in data,
                },
            )
            flash("Client updated successfully", "success")
            return redirect(url_for("client.view_client", client_id=client_id))
        else:
            flash(f"Error updating client: {message}", "danger")
            form_payload = {
                "username": data.get("username"),
                "plan_id": plan_id_value,
                "template_id": template_id_value,
                "status": data.get("status"),
                "plan_activation_date": plan_activation_date,
                "plan_expiration_date": plan_expiration_date,
            }
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
                form_data=form_payload,
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

    AuditService.log_action(
        action="create",
        entity_type="payout",
        entity_id=payout_id,
        details={
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
