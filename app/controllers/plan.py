from bson import ObjectId
from flask import Blueprint, abort, flash, redirect, request, url_for
from flask_login import current_user, login_required

from app.controllers.auth import admin_required
from app.models.plan import Plan
from app.services.audit_service import AuditService
from app.views.plan_view import PlanView

plan = Blueprint("plan", __name__, url_prefix="/plans")


@plan.route("/")
@login_required
@admin_required
def list_plans():
    """List all plans"""
    plans = Plan.get_all()
    return PlanView.render_list(plans)


@plan.route("/create", methods=["GET", "POST"])
@login_required
@admin_required
def create_plan():
    """Create a new plan"""
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        price = request.form.get("price")
        duration_days = request.form.get("duration_days")

        if not name or not price or not duration_days:
            flash("Please fill all required fields", "danger")
            return PlanView.render_create_form(
                form_data={
                    "name": name,
                    "description": description,
                    "price": price,
                    "duration_days": duration_days,
                }
            )

        # Create plan
        success, message = Plan.create(name, description, price, duration_days)

        if success:
            # Log plan creation in audit trail
            AuditService.log_plan_action("create", message, {"name": name, "price": price})
            flash("Plan created successfully", "success")
            return redirect(url_for("plan.list_plans"))
        else:
            flash(f"Error creating plan: {message}", "danger")

    return PlanView.render_create_form()


@plan.route("/edit/<plan_id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_plan(plan_id):
    """Edit plan information"""
    plan_data = Plan.get_by_id(plan_id)
    if not plan_data:
        flash("Plan not found", "danger")
        return redirect(url_for("plan.list_plans"))

    if request.method == "POST":
        data = {
            "name": request.form.get("name"),
            "description": request.form.get("description"),
            "price": request.form.get("price"),
            "duration_days": request.form.get("duration_days"),
        }

        # Update plan
        success, message = Plan.update(plan_id, data)

        if success:
            # Log plan update in audit trail
            AuditService.log_plan_action(
                "update",
                plan_id,
                {
                    "name": data.get("name"),
                    "price": data.get("price"),
                    "duration_days": data.get("duration_days"),
                },
            )
            flash("Plan updated successfully", "success")
            return redirect(url_for("plan.list_plans"))
        else:
            flash(f"Error updating plan: {message}", "danger")

    return PlanView.render_edit_form(plan_data)


@plan.route("/delete/<plan_id>", methods=["POST"])
@login_required
@admin_required
def delete_plan(plan_id):
    """Delete a plan"""
    if request.method == "POST":
        # Get plan data before deletion for audit log
        plan_data = Plan.get_by_id(plan_id)
        plan_name = plan_data.get("name", "unknown") if plan_data else "unknown"

        success, message = Plan.delete(plan_id)

        if success:
            # Log plan deletion in audit trail
            AuditService.log_plan_action("delete", plan_id, {"name": plan_name})
            flash("Plan deleted successfully", "success")
        else:
            flash(f"Error deleting plan: {message}", "danger")

    return redirect(url_for("plan.list_plans"))


@plan.route("/view/<plan_id>")
@login_required
@admin_required
def view_plan(plan_id):
    """View plan details"""
    plan_data = Plan.get_by_id(plan_id)
    if not plan_data:
        flash("Plan not found", "danger")
        return redirect(url_for("plan.list_plans"))

    return PlanView.render_view(plan_data)
