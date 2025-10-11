from flask import Blueprint, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.controllers.auth import admin_required
from app.models.template import Template
from app.views.template_view import TemplateView
from app.services.audit_service import AuditService
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
            # Log template creation in audit trail
            AuditService.log_template_action('create', message, {
                'name': name,
                'description': description,
                'status': status
            })
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
        # Build the data object with all new fields
        data = {
            'name': request.form.get('name'),
            'description': request.form.get('description'),
            'status': request.form.get('status', 'active')
        }
        
        # Header configuration
        data['header'] = {
            'enabled': request.form.get('header[enabled]') == 'on',
            'content': request.form.get('header[content]', ''),
            'logo': request.form.get('header[logo]', ''),
            'backgroundColor': request.form.get('header[backgroundColor]', '#ffffff')
        }
        
        # Footer configuration
        data['footer'] = {
            'enabled': request.form.get('footer[enabled]') == 'on',
            'content': request.form.get('footer[content]', ''),
            'backgroundColor': request.form.get('footer[backgroundColor]', '#f8f9fa')
        }
        
        # Versions configuration
        data['versions'] = {
            'mobile': {
                'enabled': request.form.get('versions[mobile][enabled]') == 'on',
                'customCss': request.form.get('versions[mobile][customCss]', ''),
                'customJs': request.form.get('versions[mobile][customJs]', '')
            },
            'desktop': {
                'enabled': request.form.get('versions[desktop][enabled]') == 'on',
                'customCss': request.form.get('versions[desktop][customCss]', ''),
                'customJs': request.form.get('versions[desktop][customJs]', '')
            }
        }
        
        # Pages configuration
        pages = []
        page_index = 0
        while True:
            page_id = request.form.get(f'pages[{page_index}][id]')
            if page_id is None:
                break
            
            page_type = request.form.get(f'pages[{page_index}][type]')
            page_data = {
                'id': page_id,
                'name': request.form.get(f'pages[{page_index}][name]', ''),
                'type': page_type,
                'content': request.form.get(f'pages[{page_index}][content]', '')
            }
            
            # Check if this is a required page
            if page_type in ['home', 'splashscreen']:
                page_data['required'] = True
            
            # Add login types for login pages
            if page_type == 'login':
                login_types = request.form.getlist(f'pages[{page_index}][loginTypes][]')
                page_data['loginTypes'] = login_types
            
            # Add duration for splashscreen
            if page_type == 'splashscreen':
                duration = request.form.get(f'pages[{page_index}][duration]')
                page_data['duration'] = int(duration) if duration else 3000
            
            pages.append(page_data)
            page_index += 1
        
        data['pages'] = pages
        
        # Update template
        success, message = Template.update(template_id, data)
        
        if success:
            # Log template update in audit trail
            AuditService.log_template_action('update', template_id, {
                'name': data.get('name'),
                'description': data.get('description'),
                'status': data.get('status'),
                'pages_count': len(pages)
            })
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
        # Get template data before deletion for audit log
        template_data = Template.get_by_id(template_id)
        template_name = template_data.get('name', 'unknown') if template_data else 'unknown'
        
        success, message = Template.delete(template_id)
        
        if success:
            # Log template deletion in audit trail
            AuditService.log_template_action('delete', template_id, {'name': template_name})
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