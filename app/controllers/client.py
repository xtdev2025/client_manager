from flask import Blueprint, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.controllers.auth import admin_required, super_admin_required
from app.models.client import Client
from app.models.plan import Plan
from app.models.template import Template
from app.models.user import User
from app.models.domain import Domain
from app.views.client_view import ClientView
from app.services.audit_service import AuditService
from bson import ObjectId

client = Blueprint('client', __name__, url_prefix='/clients')

@client.route('/')
@login_required
@admin_required
def list_clients():
    """List all clients"""
    clients = Client.get_all()
    
    # ClientView handles enriching client data with plan information
    return ClientView.render_list(clients)

@client.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_client():
    """Create a new client"""
    plans = Plan.get_all()
    templates = Template.get_all()
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        plan_id = request.form.get('plan_id') or None
        template_id = request.form.get('template_id') or None
        status = request.form.get('status', 'active')
        plan_activation_date = request.form.get('plan_activation_date') or None
        plan_expiration_date = request.form.get('plan_expiration_date') or None

        form_payload = {
            'username': username,
            'plan_id': plan_id,
            'template_id': template_id,
            'status': status,
            'plan_activation_date': plan_activation_date,
            'plan_expiration_date': plan_expiration_date
        }
        
        if not username or not password:
            flash('Please provide username and password', 'danger')
            return ClientView.render_create_form(
                plans,
                templates,
                form_data=form_payload
            )
        
        # Create client
        success, message = Client.create(
            username,
            password,
            plan_id,
            template_id,
            status,
            plan_activation_date=plan_activation_date,
            plan_expiration_date=plan_expiration_date
        )
        
        if success:
            # Log client creation in audit trail
            AuditService.log_client_action('create', message, {
                'username': username,
                'plan_id': plan_id,
                'template_id': template_id,
                'status': status
            })
            flash('Client created successfully', 'success')
            return redirect(url_for('client.list_clients'))
        else:
            flash(f'Error creating client: {message}', 'danger')
            return ClientView.render_create_form(
                plans,
                templates,
                form_data=form_payload
            )
    
    return ClientView.render_create_form(plans, templates)

@client.route('/edit/<client_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_client(client_id):
    """Edit client information"""
    client_data = Client.get_by_id(client_id)
    if not client_data:
        flash('Client not found', 'danger')
        return redirect(url_for('client.list_clients'))
    
    plans = Plan.get_all()
    templates = Template.get_all()
    
    if request.method == 'POST':
        plan_activation_date = request.form.get('plan_activation_date') or None
        plan_expiration_date = request.form.get('plan_expiration_date') or None

        plan_id_value = request.form.get('plan_id') or None
        template_id_value = request.form.get('template_id') or None

        data = {
            'username': request.form.get('username'),
            'plan_id': plan_id_value,
            'template_id': template_id_value,
            'status': request.form.get('status'),
            'plan_activation_date': plan_activation_date,
            'plan_expiration_date': plan_expiration_date
        }
        
        # Only update password if provided
        if request.form.get('password'):
            data['password'] = request.form.get('password')
        
        # Update client
        success, message = Client.update(client_id, data)
        
        if success:
            # Log client update in audit trail
            AuditService.log_client_action('update', client_id, {
                'username': data.get('username'),
                'plan_id': plan_id_value,
                'status': data.get('status'),
                'password_changed': 'password' in data
            })
            flash('Client updated successfully', 'success')
            return redirect(url_for('client.list_clients'))
        else:
            flash(f'Error updating client: {message}', 'danger')
            form_payload = {
                'username': data.get('username'),
                'plan_id': plan_id_value,
                'template_id': template_id_value,
                'status': data.get('status'),
                'plan_activation_date': plan_activation_date,
                'plan_expiration_date': plan_expiration_date
            }
            return ClientView.render_edit_form(client_data, plans, templates, form_data=form_payload)
    
    return ClientView.render_edit_form(client_data, plans, templates)

@client.route('/delete/<client_id>', methods=['POST'])
@login_required
@admin_required
def delete_client(client_id):
    """Delete a client"""
    if request.method == 'POST':
        # Get client data before deletion for audit log
        client_data = Client.get_by_id(client_id)
        username = client_data.get('username', 'unknown') if client_data else 'unknown'
        
        success, message = Client.delete(client_id)
        
        if success:
            # Log client deletion in audit trail
            AuditService.log_client_action('delete', client_id, {'username': username})
            flash('Client deleted successfully', 'success')
        else:
            flash(f'Error deleting client: {message}', 'danger')
    
    return redirect(url_for('client.list_clients'))

@client.route('/view/<client_id>')
@login_required
@admin_required
def view_client(client_id):
    """View client details"""
    client_data = Client.get_by_id(client_id)
    if not client_data:
        flash('Client not found', 'danger')
        return redirect(url_for('client.list_clients'))
    
    # ClientView handles enriching client data with plan information
    return ClientView.render_view(client_data)

@client.route('/<client_id>/domains')
@login_required
@admin_required
def manage_domains(client_id):
    """Manage domains for a client"""
    client_data = Client.get_by_id(client_id)
    if not client_data:
        flash('Client not found', 'danger')
        return redirect(url_for('client.list_clients'))
    
    # Get client domains
    client_domains = Domain.get_client_domains(client_id)
    
    # Get all available domains for assignment
    available_domains = Domain.get_all()
    
    # Get domain limit (using the first domain's limit as default)
    domain_limit = 5  # Default
    if available_domains:
        domain_limit = available_domains[0].get('domain_limit', 5)
    
    return ClientView.render_domains(client_data, client_domains, available_domains, domain_limit)

@client.route('/<client_id>/domains/add', methods=['POST'])
@login_required
@super_admin_required
def add_domain(client_id):
    """Add a domain to a client"""
    if request.method == 'POST':
        domain_id = request.form.get('domain_id')
        subdomain = request.form.get('subdomain')
        
        if not domain_id or not subdomain:
            flash('Please provide both domain and subdomain', 'danger')
            return redirect(url_for('client.manage_domains', client_id=client_id))
        
        # Assign domain to client
        success, message = Domain.assign_to_client(client_id, domain_id, subdomain)
        
        if success:
            flash('Domain assigned successfully', 'success')
        else:
            flash(f'Error assigning domain: {message}', 'danger')
    
    return redirect(url_for('client.manage_domains', client_id=client_id))

@client.route('/<client_id>/domains/remove/<client_domain_id>', methods=['POST'])
@login_required
@super_admin_required
def remove_domain(client_id, client_domain_id):
    """Remove a domain from a client"""
    if request.method == 'POST':
        # Remove domain from client
        success, message = Domain.remove_from_client(client_id, client_domain_id)
        
        if success:
            flash('Domain removed successfully', 'success')
        else:
            flash(f'Error removing domain: {message}', 'danger')
    
    return redirect(url_for('client.manage_domains', client_id=client_id))