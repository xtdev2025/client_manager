from flask import Blueprint, flash, redirect, url_for
from flask_login import login_required

from app.controllers.auth import admin_required
from app.controllers.crud_mixin import CrudControllerMixin
from app.models.plan import Plan
from app.repositories.base import ModelCrudRepository
from app.schemas.plan import PlanCreateSchema, PlanUpdateSchema
from app.views.plan_view import PlanView

plan = Blueprint("plan", __name__, url_prefix="/plans")


class PlanCrudController(CrudControllerMixin):
    entity_name = "Plan"
    audit_entity = "plan"
    list_endpoint = "plan.list_plans"
    detail_endpoint = "plan.view_plan"
    create_schema = PlanCreateSchema
    update_schema = PlanUpdateSchema
    view = PlanView


plan_crud = PlanCrudController(ModelCrudRepository(Plan))


@plan.route("/")
@login_required
@admin_required
def list_plans():
    """List all plans"""
    return plan_crud.list_view()


@plan.route("/create", methods=["GET", "POST"])
@login_required
@admin_required
def create_plan():
    """Create a new plan"""
    return plan_crud.create_view()


@plan.route("/edit/<plan_id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_plan(plan_id):
    """Edit plan information"""
    return plan_crud.edit_view(plan_id)


@plan.route("/delete/<plan_id>", methods=["POST"])
@login_required
@admin_required
def delete_plan(plan_id):
    """Delete a plan"""
    return plan_crud.delete_view(plan_id)


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
