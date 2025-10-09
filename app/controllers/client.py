from flask import Blueprint, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.controllers.auth import admin_required
from app.models.client import Client
from app.models.plan import Plan
from app.models.user import User
from app.views.client_view import ClientView
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
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        plan_id = request.form.get('plan_id') or None
        status = request.form.get('status', 'active')
        
        if not username or not password:
            flash('Please provide username and password', 'danger')
            return ClientView.render_create_form(
                plans, 
                form_data={'username': username, 'plan_id': plan_id, 'status': status}
            )
        
        # Create client
        success, message = Client.create(username, password, plan_id, status)
        
        if success:
            flash('Client created successfully', 'success')
            return redirect(url_for('client.list_clients'))
        else:
            flash(f'Error creating client: {message}', 'danger')
    
    return ClientView.render_create_form(plans)

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
    
    if request.method == 'POST':
        data = {
            'username': request.form.get('username'),
            'plan_id': request.form.get('plan_id') or None,
            'status': request.form.get('status')
        }
        
        # Only update password if provided
        if request.form.get('password'):
            data['password'] = request.form.get('password')
        
        # Update client
        success, message = Client.update(client_id, data)
        
        if success:
            flash('Client updated successfully', 'success')
            return redirect(url_for('client.list_clients'))
        else:
            flash(f'Error updating client: {message}', 'danger')
    
    return ClientView.render_edit_form(client_data, plans)

@client.route('/delete/<client_id>', methods=['POST'])
@login_required
@admin_required
def delete_client(client_id):
    """Delete a client"""
    if request.method == 'POST':
        success, message = Client.delete(client_id)
        
        if success:
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