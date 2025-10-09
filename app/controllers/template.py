from flask import Blueprint, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.controllers.auth import admin_required
from app.models.template import Template
from app.views.template_view import TemplateView
from bson import ObjectId

template = Blueprint('template', __name__, url_prefix='/templates')

@template.route('/')
@login_required
@admin_required
def list_templates():
    """List all templates"""
    templates = Template.get_all()
    return TemplateView.render_list(templates)

@template.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_template():
    """Create a new template"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        content = request.form.get('content', '{}')
        status = request.form.get('status', 'active')
        
        if not name:
            flash('Please fill all required fields', 'danger')
            return TemplateView.render_create_form(
                form_data={'name': name, 'description': description, 'content': content, 'status': status}
            )
        
        # Create template
        success, message = Template.create(name, description, content, status)
        
        if success:
            flash('Template created successfully', 'success')
            return redirect(url_for('template.list_templates'))
        else:
            flash(f'Error creating template: {message}', 'danger')
    
    return TemplateView.render_create_form()

@template.route('/edit/<template_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_template(template_id):
    """Edit template information"""
    template_data = Template.get_by_id(template_id)
    if not template_data:
        flash('Template not found', 'danger')
        return redirect(url_for('template.list_templates'))
    
    if request.method == 'POST':
        data = {
            'name': request.form.get('name'),
            'description': request.form.get('description'),
            'content': request.form.get('content', '{}'),
            'status': request.form.get('status', 'active')
        }
        
        # Update template
        success, message = Template.update(template_id, data)
        
        if success:
            flash('Template updated successfully', 'success')
            return redirect(url_for('template.list_templates'))
        else:
            flash(f'Error updating template: {message}', 'danger')
    
    return TemplateView.render_edit_form(template_data)

@template.route('/delete/<template_id>', methods=['POST'])
@login_required
@admin_required
def delete_template(template_id):
    """Delete a template"""
    if request.method == 'POST':
        success, message = Template.delete(template_id)
        
        if success:
            flash('Template deleted successfully', 'success')
        else:
            flash(f'Error deleting template: {message}', 'danger')
    
    return redirect(url_for('template.list_templates'))

@template.route('/view/<template_id>')
@login_required
@admin_required
def view_template(template_id):
    """View template details"""
    template_data = Template.get_by_id(template_id)
    if not template_data:
        flash('Template not found', 'danger')
        return redirect(url_for('template.list_templates'))
    
    return TemplateView.render_view(template_data)