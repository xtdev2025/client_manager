from datetime import datetime

from bson import ObjectId
from flask import Blueprint, abort, flash, redirect, request, url_for
from flask_login import current_user, login_required

from app.controllers.auth import admin_required, super_admin_required
from app.models.admin import Admin
from app.models.user import User
from app.services.audit_service import AuditService
from app.views.admin_view import AdminView

admin = Blueprint("admin", __name__, url_prefix="/admins")


@admin.route("/")
@login_required
@admin_required
def list_admins():
    """List all admins"""
    admins = Admin.get_all()
    return AdminView.render_list(admins)


@admin.route("/create", methods=["GET", "POST"])
@login_required
@super_admin_required
def create_admin():
    """Create a new admin (only super_admin can do this)"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        role = request.form.get("role", "admin")

        if not username or not password:
            flash("Please provide username and password", "danger")
            return AdminView.render_create_form(form_data={"username": username, "role": role})

        # Create admin
        success, message = Admin.create(username, password, role)

        if success:
            # Log admin creation in audit trail
            AuditService.log_admin_action("create", message, {"username": username, "role": role})
            flash("Admin created successfully", "success")
            return redirect(url_for("admin.list_admins"))
        else:
            flash(f"Error creating admin: {message}", "danger")

    return AdminView.render_create_form()


@admin.route("/edit/<admin_id>", methods=["GET", "POST"])
@login_required
@super_admin_required
def edit_admin(admin_id):
    """Edit admin information (only super_admin can do this)"""
    admin_data = Admin.get_by_id(admin_id)
    if not admin_data:
        flash("Admin not found", "danger")
        return redirect(url_for("admin.list_admins"))

    # Check if trying to edit themselves
    if str(admin_data["_id"]) == current_user.id:
        flash("You cannot edit your own account from this page", "warning")
        return redirect(url_for("admin.list_admins"))

    if request.method == "POST":
        data = {"username": request.form.get("username"), "role": request.form.get("role")}

        # Only update password if provided
        if request.form.get("password"):
            data["password"] = request.form.get("password")

        # Update admin
        success, message = Admin.update(admin_id, data)

        if success:
            # Log admin update in audit trail
            AuditService.log_admin_action("update", admin_id, {"username": data.get("username")})
            flash("Admin updated successfully", "success")
            return redirect(url_for("admin.list_admins"))
        else:
            flash(f"Error updating admin: {message}", "danger")

    return AdminView.render_edit_form(admin_data)


@admin.route("/delete/<admin_id>", methods=["POST"])
@login_required
@super_admin_required
def delete_admin(admin_id):
    """Delete an admin (only super_admin can do this)"""
    # Check if trying to delete themselves
    if admin_id == current_user.id:
        flash("You cannot delete your own account", "danger")
        return redirect(url_for("admin.list_admins"))

    if request.method == "POST":
        # Get admin data before deletion for audit log
        admin_data = Admin.get_by_id(admin_id)
        username = admin_data.get("username", "unknown") if admin_data else "unknown"

        success, message = Admin.delete(admin_id)

        if success:
            # Log admin deletion in audit trail
            AuditService.log_admin_action("delete", admin_id, {"username": username})
            flash("Admin deleted successfully", "success")
        else:
            flash(f"Error deleting admin: {message}", "danger")

    return redirect(url_for("admin.list_admins"))


@admin.route("/profile", methods=["GET", "POST"])
@login_required
@admin_required
def profile():
    """Edit own profile (for any admin)"""
    admin_data = Admin.get_by_id(current_user.id)
    if not admin_data:
        flash("Admin not found", "danger")
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        # Only allow password change for own profile
        if request.form.get("password"):
            data = {"password": request.form.get("password")}

            # Update admin
            success, message = Admin.update(current_user.id, data)

            if success:
                flash("Password updated successfully", "success")
            else:
                flash(f"Error updating password: {message}", "danger")

    return AdminView.render_profile(admin_data)


@admin.route("/audit-logs")
@login_required
@admin_required
def audit_logs():
    """View audit logs with filtering and pagination"""
    # Get filter parameters
    entity_type = request.args.get("entity_type", "")
    action = request.args.get("action", "")
    user_id = request.args.get("user_id", "")
    start_date_str = request.args.get("start_date", "")
    end_date_str = request.args.get("end_date", "")

    # Pagination
    page = request.args.get("page", 1, type=int)
    per_page = 50

    # Parse dates
    start_date = None
    end_date = None
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        except ValueError:
            flash("Invalid start date format", "warning")

    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
            # Set to end of day
            end_date = end_date.replace(hour=23, minute=59, second=59)
        except ValueError:
            flash("Invalid end date format", "warning")

    # Get logs with filters
    logs, total = AuditService.get_recent_logs(
        limit=per_page,
        entity_type=entity_type if entity_type else None,
        action=action if action else None,
        user_id=user_id if user_id else None,
        start_date=start_date,
        end_date=end_date,
        page=page,
    )

    # Debug logging
    from flask import current_app

    current_app.logger.info(
        f"Audit logs query returned {total} total logs, {len(logs)} on page {page}"
    )

    # Calculate pagination
    total_pages = (total + per_page - 1) // per_page

    # Get all admins for user filter dropdown
    admins = Admin.get_all()

    return AdminView.render_audit_logs(
        logs=logs,
        admins=admins,
        total=total,
        page=page,
        total_pages=total_pages,
        per_page=per_page,
        filters={
            "entity_type": entity_type,
            "action": action,
            "user_id": user_id,
            "start_date": start_date_str,
            "end_date": end_date_str,
        },
    )


@admin.route("/clear-audit-logs", methods=["POST"])
@login_required
@super_admin_required
def clear_audit_logs():
    """Clear all audit logs (only super_admin can do this)"""
    try:
        # Get count before deletion for confirmation message
        from app import mongo

        count = mongo.db.audit_logs.count_documents({})

        # Delete all audit logs
        result = mongo.db.audit_logs.delete_many({})

        # Log this critical action (creates a new log entry after clearing)
        AuditService.log_admin_action(
            "delete_all",
            "audit_logs",
            {
                "deleted_count": result.deleted_count,
                "previous_count": count,
                "reason": "Manual clear all logs by super admin",
            },
        )

        flash(f"Successfully deleted {result.deleted_count} audit log entries", "success")
    except Exception as e:
        flash(f"Error clearing audit logs: {str(e)}", "danger")

    return redirect(url_for("admin.audit_logs"))
