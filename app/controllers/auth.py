from flask import Blueprint, redirect, url_for, flash, request, session
from flask_login import login_user, current_user, logout_user, login_required
from app.models.user import User
from app.models.admin import Admin
from app.models.client import Client
from app.views.auth_view import AuthView
from functools import wraps
import bson

auth = Blueprint('auth', __name__)

def admin_required(f):
    """Decorator for routes that require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        
        user = User.get_by_id(current_user.id)
        if not user or 'role' not in user or user['role'] not in ['admin', 'super_admin']:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def super_admin_required(f):
    """Decorator for routes that require super admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        
        user = User.get_by_id(current_user.id)
        if not user or 'role' not in user or user['role'] != 'super_admin':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Login route"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please provide both username and password', 'danger')
            return AuthView.render_login(form_data={'username': username})
        
        user = User.get_by_username(username)
        
        if user and User.check_password(user, password):
            # Store user type and role in session
            session['user_type'] = user.get('user_type', 'client')
            session['role'] = user.get('role', 'client')
            
            # Handle client-specific validation
            if session['user_type'] == 'client':
                if user.get('status') != 'active':
                    flash('Your account is not active. Please contact support.', 'warning')
                    return AuthView.render_login(form_data={'username': username})
            
            # Create a User object for Flask-Login
            from app.utils.user_loader import UserObject
            user_obj = UserObject(str(user['_id']))
            login_user(user_obj, remember=True)
            
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page if next_page else url_for('main.dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return AuthView.render_login()

@auth.route('/logout')
@login_required
def logout():
    """Logout route"""
    logout_user()
    session.pop('user_type', None)
    session.pop('role', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """Register route for clients"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not username or not password or not confirm_password:
            flash('Please fill out all fields', 'danger')
            return AuthView.render_register(form_data={'username': username})
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return AuthView.render_register(form_data={'username': username})
        
        # Check if username already exists
        if User.get_by_username(username):
            flash('Username already exists', 'danger')
            return AuthView.render_register(form_data={'username': username})
        
        # Create client with default plan (None for now)
        success, message = Client.create(username, password, None)
        
        if success:
            flash('Registration successful! You can now login.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(f'Registration failed: {message}', 'danger')
    
    return AuthView.render_register()

@auth.route('/register_admin', methods=['GET', 'POST'])
@login_required
@super_admin_required
def register_admin():
    """Register route for admins (only accessible by super_admin)"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role', 'admin')
        
        if not username or not password or not confirm_password:
            flash('Please fill out all fields', 'danger')
            return AuthView.render_register_admin(form_data={'username': username})
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return AuthView.render_register_admin(form_data={'username': username, 'role': role})
        
        # Check if username already exists
        if User.get_by_username(username):
            flash('Username already exists', 'danger')
            return AuthView.render_register_admin(form_data={'username': username, 'role': role})
        
        # Create admin
        success, message = Admin.create(username, password, role)
        
        if success:
            flash('Admin registration successful!', 'success')
            return redirect(url_for('admin.list_admins'))
        else:
            flash(f'Registration failed: {message}', 'danger')
    
    return AuthView.render_register_admin()