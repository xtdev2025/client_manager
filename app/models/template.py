from flask import current_app
from bson.objectid import ObjectId
from datetime import datetime
from app import mongo

class Template:
    """Template model for client templates"""
    
    @staticmethod
    def create(name, description, content=None, status='active'):
        """Create a new template"""
        try:
            # Create template object
            new_template = {
                'name': name,
                'description': description,
                'content': content or {},
                'status': status,
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