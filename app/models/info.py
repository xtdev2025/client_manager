from flask import current_app
from bson.objectid import ObjectId
from datetime import datetime
from app import mongo

class Info:
    """Model for client information like bank accounts, passwords, etc."""
    
    @staticmethod
    def create(client_id, agencia, conta, senha, senha6, senha4, anotacoes=None, 
               saldo=0.0, template_id=None, domain_id=None, status='active'):
        """Create a new info entry"""
        try:
            if isinstance(client_id, str):
                client_id = ObjectId(client_id)
            if template_id and isinstance(template_id, str):
                template_id = ObjectId(template_id)
            if domain_id and isinstance(domain_id, str):
                domain_id = ObjectId(domain_id)
                
            # Create info object
            new_info = {
                'client_id': client_id,
                'agencia': agencia,
                'conta': conta,
                'senha': senha,
                'senha6': senha6,
                'senha4': senha4,
                'anotacoes': anotacoes,
                'saldo': float(saldo) if saldo else 0.0,
                'template_id': template_id,
                'domain_id': domain_id,
                'status': status,
                'createdAt': datetime.utcnow(),
                'updatedAt': datetime.utcnow()
            }
            
            # Insert into database
            result = mongo.db.infos.insert_one(new_info)
            
            if result.inserted_id:
                return True, str(result.inserted_id)
            return False, "Database error"
        
        except Exception as e:
            current_app.logger.error(f"Error creating info: {e}")
            return False, str(e)
    
    @staticmethod
    def update(info_id, data):
        """Update info information"""
        try:
            if isinstance(info_id, str):
                info_id = ObjectId(info_id)
            
            # Handle special fields
            if 'client_id' in data and isinstance(data['client_id'], str):
                data['client_id'] = ObjectId(data['client_id'])
            if 'template_id' in data and data['template_id'] and isinstance(data['template_id'], str):
                data['template_id'] = ObjectId(data['template_id'])
            if 'domain_id' in data and data['domain_id'] and isinstance(data['domain_id'], str):
                data['domain_id'] = ObjectId(data['domain_id'])
            if 'saldo' in data:
                data['saldo'] = float(data['saldo']) if data['saldo'] else 0.0
            
            # Add updated timestamp
            data['updatedAt'] = datetime.utcnow()
            
            result = mongo.db.infos.update_one(
                {'_id': info_id},
                {'$set': data}
            )
            
            if result.modified_count > 0:
                return True, "Info updated successfully"
            return False, "No changes made or info not found"
            
        except Exception as e:
            current_app.logger.error(f"Error updating info: {e}")
            return False, str(e)
    
    @staticmethod
    def delete(info_id):
        """Delete an info entry"""
        try:
            if isinstance(info_id, str):
                info_id = ObjectId(info_id)
                
            result = mongo.db.infos.delete_one({'_id': info_id})
            
            if result.deleted_count > 0:
                return True, "Info deleted successfully"
            return False, "Info not found"
            
        except Exception as e:
            current_app.logger.error(f"Error deleting info: {e}")
            return False, str(e)
    
    @staticmethod
    def get_all():
        """Get all info entries"""
        try:
            infos = list(mongo.db.infos.find())
            return infos
        except Exception as e:
            current_app.logger.error(f"Error getting infos: {e}")
            return []
    
    @staticmethod
    def get_by_id(info_id):
        """Get info by ID"""
        try:
            if isinstance(info_id, str):
                info_id = ObjectId(info_id)
                
            info = mongo.db.infos.find_one({'_id': info_id})
            return info
        except Exception as e:
            current_app.logger.error(f"Error getting info by ID: {e}")
            return None
    
    @staticmethod
    def get_by_client(client_id):
        """Get all info entries for a specific client"""
        try:
            if isinstance(client_id, str):
                client_id = ObjectId(client_id)
                
            infos = list(mongo.db.infos.find({'client_id': client_id}))
            return infos
        except Exception as e:
            current_app.logger.error(f"Error getting client infos: {e}")
            return []
    
    @staticmethod
    def count_by_client(client_id):
        """Count how many info entries a client has"""
        try:
            if isinstance(client_id, str):
                client_id = ObjectId(client_id)
                
            count = mongo.db.infos.count_documents({'client_id': client_id})
            return count
        except Exception as e:
            current_app.logger.error(f"Error counting client infos: {e}")
            return 0
    
    @staticmethod
    def get_with_relations(info_id):
        """Get info with related client, template and domain data"""
        try:
            if isinstance(info_id, str):
                info_id = ObjectId(info_id)
                
            info = mongo.db.infos.find_one({'_id': info_id})
            if not info:
                return None
                
            # Enrich with client info
            if 'client_id' in info:
                from app.models.client import Client
                client = Client.get_by_id(info['client_id'])
                if client:
                    info['client'] = client
            
            # Enrich with template info
            if 'template_id' in info and info['template_id']:
                from app.models.template import Template
                template = Template.get_by_id(info['template_id'])
                if template:
                    info['template'] = template
            
            # Enrich with domain info
            if 'domain_id' in info and info['domain_id']:
                from app.models.domain import Domain
                domain = Domain.get_by_id(info['domain_id'])
                if domain:
                    info['domain'] = domain
            
            return info
        except Exception as e:
            current_app.logger.error(f"Error getting info with relations: {e}")
            return None