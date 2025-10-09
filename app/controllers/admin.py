from flask import Blueprint, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.controllers.auth import admin_required, super_admin_required
from app.models.admin import Admin
from app.models.user import User
from app.views.admin_view import AdminView
from bson import ObjectId

admin = Blueprint('admin', __name__, url_prefix='/admins')

@admin.route('/')
@login_required
@admin_required
def list_admins():
    """List all admins"""
    admins = Admin.get_all()
    return AdminView.render_list(admins)

@admin.route('/create', methods=['GET', 'POST'])
@login_required
@super_admin_required
def create_admin():
    """Create a new admin (only super_admin can do this)"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role', 'admin')
        
        if not username or not password:
            flash('Please provide username and password', 'danger')
            return AdminView.render_create_form(form_data={'username': username, 'role': role})
        
        # Create admin
        success, message = Admin.create(username, password, role)
        
        if success:
            flash('Admin created successfully', 'success')
            return redirect(url_for('admin.list_admins'))
        else:
            flash(f'Error creating admin: {message}', 'danger')
    
    return AdminView.render_create_form()

@admin.route('/edit/<admin_id>', methods=['GET', 'POST'])
@login_required
@super_admin_required
def edit_admin(admin_id):
    """Edit admin information (only super_admin can do this)"""
    admin_data = Admin.get_by_id(admin_id)
    if not admin_data:
        flash('Admin not found', 'danger')
        return redirect(url_for('admin.list_admins'))
    
    # Check if trying to edit themselves
    if str(admin_data['_id']) == current_user.id:
        flash('You cannot edit your own account from this page', 'warning')
        return redirect(url_for('admin.list_admins'))
    
    if request.method == 'POST':
        data = {
            'username': request.form.get('username'),
            'role': request.form.get('role')
        }
        
        # Only update password if provided
        if request.form.get('password'):
            data['password'] = request.form.get('password')
        
        # Update admin
        success, message = Admin.update(admin_id, data)
        
        if success:
            flash('Admin updated successfully', 'success')
            return redirect(url_for('admin.list_admins'))
        else:
            flash(f'Error updating admin: {message}', 'danger')
    
    return AdminView.render_edit_form(admin_data)

@admin.route('/delete/<admin_id>', methods=['POST'])
@login_required
@super_admin_required
def delete_admin(admin_id):
    """Delete an admin (only super_admin can do this)"""
    # Check if trying to delete themselves
    if admin_id == current_user.id:
        flash('You cannot delete your own account', 'danger')
        return redirect(url_for('admin.list_admins'))
    
    if request.method == 'POST':
        success, message = Admin.delete(admin_id)
        
        if success:
            flash('Admin deleted successfully', 'success')
        else:
            flash(f'Error deleting admin: {message}', 'danger')
    
    return redirect(url_for('admin.list_admins'))

@admin.route('/profile', methods=['GET', 'POST'])
@login_required
@admin_required
def profile():
    """Edit own profile (for any admin)"""
    admin_data = Admin.get_by_id(current_user.id)
    if not admin_data:
        flash('Admin not found', 'danger')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        # Only allow password change for own profile
        if request.form.get('password'):
            data = {
                'password': request.form.get('password')
            }
            
            # Update admin
            success, message = Admin.update(current_user.id, data)
            
            if success:
                flash('Password updated successfully', 'success')
            else:
                flash(f'Error updating password: {message}', 'danger')
    
    return AdminView.render_profile(admin_data)