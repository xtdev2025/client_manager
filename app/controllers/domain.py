from bson import ObjectId
from flask import Blueprint, abort, flash, redirect, request, url_for
from flask_login import current_user, login_required

from app import mongo
from app.controllers.auth import admin_required, super_admin_required
from app.models.domain import Domain
from app.services.audit_service import AuditService
from app.views.domain_view import DomainView

domain = Blueprint("domain", __name__, url_prefix="/domains")


@domain.route("/")
@login_required
@admin_required
def list_domains():
    """List all domains with subdomain counts"""
    domains = Domain.get_all()

    # Enrich domains with subdomain counts
    enriched_domains = []
    for domain in domains:
        domain_id = domain["_id"]
        subdomain_count = mongo.db.client_domains.count_documents({"domain_id": domain_id})
        domain["subdomain_count"] = subdomain_count
        domain["available_slots"] = domain.get("domain_limit", 5) - subdomain_count
        enriched_domains.append(domain)

    return DomainView.render_list(enriched_domains)


@domain.route("/create", methods=["GET", "POST"])
@login_required
@super_admin_required
def create_domain():
    """Create a new domain"""
    if request.method == "POST":
        name = request.form.get("name")
        cloudflare_api = request.form.get("cloudflare_api")
        cloudflare_email = request.form.get("cloudflare_email")
        cloudflare_password = request.form.get("cloudflare_password")
        cloudflare_status = request.form.get("cloudflare_status") == "on"
        ssl = request.form.get("ssl") == "on"
        domain_limit = int(request.form.get("domain_limit", 5))

        if not name:
            flash("Please provide a domain name", "danger")
            return DomainView.render_create_form(
                form_data={
                    "name": name,
                    "cloudflare_api": cloudflare_api,
                    "cloudflare_email": cloudflare_email,
                    "cloudflare_status": cloudflare_status,
                    "ssl": ssl,
                    "domain_limit": domain_limit,
                }
            )

        # Create domain
        success, message = Domain.create(
            name=name,
            cloudflare_api=cloudflare_api,
            cloudflare_email=cloudflare_email,
            cloudflare_password=cloudflare_password,
            cloudflare_status=cloudflare_status,
            ssl=ssl,
            domain_limit=domain_limit,
        )

        if success:
            # Log domain creation in audit trail
            AuditService.log_domain_action(
                "create",
                message,
                {
                    "name": name,
                    "cloudflare_status": cloudflare_status,
                    "ssl": ssl,
                    "domain_limit": domain_limit,
                },
            )
            flash("Domain created successfully", "success")
            return redirect(url_for("domain.list_domains"))
        else:
            flash(f"Error creating domain: {message}", "danger")

    return DomainView.render_create_form()


@domain.route("/edit/<domain_id>", methods=["GET", "POST"])
@login_required
@super_admin_required
def edit_domain(domain_id):
    """Edit domain information"""
    domain_data = Domain.get_by_id(domain_id)
    if not domain_data:
        flash("Domain not found", "danger")
        return redirect(url_for("domain.list_domains"))

    if request.method == "POST":
        data = {
            "name": request.form.get("name"),
            "cloudflare_api": request.form.get("cloudflare_api"),
            "cloudflare_email": request.form.get("cloudflare_email"),
            "cloudflare_status": request.form.get("cloudflare_status") == "on",
            "ssl": request.form.get("ssl") == "on",
            "domain_limit": int(request.form.get("domain_limit", 5)),
        }

        # If password is provided, update it
        if request.form.get("cloudflare_password"):
            data["cloudflare_password"] = request.form.get("cloudflare_password")

        # Update domain
        success, message = Domain.update(domain_id, data)

        if success:
            # Log domain update in audit trail
            AuditService.log_domain_action(
                "update",
                domain_id,
                {
                    "name": data.get("name"),
                    "cloudflare_status": data.get("cloudflare_status"),
                    "ssl": data.get("ssl"),
                    "domain_limit": data.get("domain_limit"),
                },
            )
            flash("Domain updated successfully", "success")
            return redirect(url_for("domain.list_domains"))
        else:
            flash(f"Error updating domain: {message}", "danger")

    return DomainView.render_edit_form(domain_data)


@domain.route("/delete/<domain_id>", methods=["POST"])
@login_required
@super_admin_required
def delete_domain(domain_id):
    """Delete a domain"""
    # Get domain data before deletion for audit log
    domain_data = Domain.get_by_id(domain_id)
    domain_name = domain_data.get("name", "unknown") if domain_data else "unknown"

    success, message = Domain.delete(domain_id)

    if success:
        # Log domain deletion in audit trail
        AuditService.log_domain_action("delete", domain_id, {"name": domain_name})
        flash("Domain deleted successfully", "success")
    else:
        flash(f"Error deleting domain: {message}", "danger")

    return redirect(url_for("domain.list_domains"))


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
