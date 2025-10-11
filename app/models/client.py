from flask import current_app
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from app import mongo, bcrypt
from app.models.user import User
from app.models.plan import Plan

class Client(User):
    """Client model for client management"""
    
    @staticmethod
    def create(username, password, plan_id, template_id=None, status='active'):
        """Create new client"""
        try:
            # Check if username already exists
            if User.get_by_username(username):
                return False, "Username already exists"
            
            # Hash password
            hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
            
            # Prepare related references
            plan_object_id = ObjectId(plan_id) if plan_id else None
            template_object_id = ObjectId(template_id) if template_id else None

            # Calculate plan expiration when applicable
            expiration_date = None
            plan_activation = None
            if plan_object_id:
                plan = Plan.get_by_id(plan_object_id)
                if plan and plan.get('duration_days'):
                    plan_activation = datetime.utcnow()
                    expiration_date = plan_activation + timedelta(days=plan.get('duration_days'))

            # Create client object
            new_client = {
                'username': username,
                'password': hashed_pw,
                'plan_id': plan_object_id,
                'template_id': template_object_id,
                'status': status,
                'role': 'client',
                'createdAt': datetime.utcnow(),
                'updatedAt': datetime.utcnow(),
                'planActivatedAt': plan_activation,
                'expiredAt': expiration_date
            }
            
            # Insert into database
            result = mongo.db.clients.insert_one(new_client)
            
            if result.inserted_id:
                return True, str(result.inserted_id)
            return False, "Database error"
        
        except Exception as e:
            current_app.logger.error(f"Error creating client: {e}")
            return False, str(e)
    
    @staticmethod
    def update(client_id, data):
        """Update client information"""
        try:
            if isinstance(client_id, str):
                client_id = ObjectId(client_id)

            existing_client = Client.get_by_id(client_id)
            if not existing_client:
                return False, "Client not found"
                
            # Ensure password is hashed if provided
            if 'password' in data:
                data['password'] = bcrypt.generate_password_hash(data['password']).decode('utf-8')
            
            # Convert plan_id to ObjectId if provided and update expiration
            if 'plan_id' in data:
                if data['plan_id']:
                    plan_object_id = ObjectId(data['plan_id'])
                    data['plan_id'] = plan_object_id

                    plan = Plan.get_by_id(plan_object_id)
                    plan_duration = plan.get('duration_days') if plan else None
                    plan_changed = existing_client.get('plan_id') != plan_object_id if existing_client else True
                    expiration_missing = not existing_client.get('expiredAt') if existing_client else True

                    if plan_duration and (plan_changed or expiration_missing):
                        activation = datetime.utcnow()
                        data['planActivatedAt'] = activation
                        data['expiredAt'] = activation + timedelta(days=plan_duration)
                    else:
                        data['planActivatedAt'] = existing_client.get('planActivatedAt')
                        data['expiredAt'] = existing_client.get('expiredAt')
                else:
                    data['plan_id'] = None
                    data['planActivatedAt'] = None
                    data['expiredAt'] = None

            # Convert template_id to ObjectId if provided
            if 'template_id' in data and data['template_id']:
                data['template_id'] = ObjectId(data['template_id'])
                
            # Add updated timestamp
            data['updatedAt'] = datetime.utcnow()
            
            result = mongo.db.clients.update_one(
                {'_id': client_id},
                {'$set': data}
            )
            
            if result.modified_count > 0:
                return True, "Client updated successfully"
            return False, "No changes made or client not found"
            
        except Exception as e:
            current_app.logger.error(f"Error updating client: {e}")
            return False, str(e)
    
    @staticmethod
    def delete(client_id):
        """Delete client"""
        try:
            if isinstance(client_id, str):
                client_id = ObjectId(client_id)
                
            result = mongo.db.clients.delete_one({'_id': client_id})
            
            if result.deleted_count > 0:
                return True, "Client deleted successfully"
            return False, "Client not found"
            
        except Exception as e:
            current_app.logger.error(f"Error deleting client: {e}")
            return False, str(e)
    
    @staticmethod
    def get_all():
        """Get all clients"""
        try:
            clients = list(mongo.db.clients.find())
            return clients
        except Exception as e:
            current_app.logger.error(f"Error getting clients: {e}")
            return []
    
    @staticmethod
    def get_by_id(client_id):
        """Get client by ID"""
        try:
            if isinstance(client_id, str):
                client_id = ObjectId(client_id)
                
            client = mongo.db.clients.find_one({'_id': client_id})
            return client
        except Exception as e:
            current_app.logger.error(f"Error getting client by ID: {e}")
            return None