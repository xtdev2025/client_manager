from flask import current_app
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from app import mongo, bcrypt
from app.models.user import User
from app.models.plan import Plan

class Client(User):
    """Client model for client management"""

    @staticmethod
    def _parse_date_input(value):
        """Parse string or datetime input into a datetime object."""
        if not value:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            candidate = value.strip()
            if not candidate:
                return None
            for fmt in ('%Y-%m-%d', '%Y-%m-%dT%H:%M'):
                try:
                    return datetime.strptime(candidate, fmt)
                except ValueError:
                    continue
        raise ValueError("Invalid date format")

    @staticmethod
    def _prepare_plan_dates(plan_object_id, activation_input=None, expiration_input=None,
                             existing_client=None, force_update=False):
        """Resolve activation and expiration dates for a plan assignment."""
        if not plan_object_id:
            return True, None, None, None

        plan = Plan.get_by_id(plan_object_id)
        if not plan:
            return False, None, None, "Associated plan not found."

        plan_duration = plan.get('duration_days')

        try:
            activation = Client._parse_date_input(activation_input)
        except ValueError:
            return False, None, None, "Invalid activation date format. Use YYYY-MM-DD."

        try:
            expiration = Client._parse_date_input(expiration_input)
        except ValueError:
            return False, None, None, "Invalid expiration date format. Use YYYY-MM-DD."

        existing_activation = existing_client.get('planActivatedAt') if existing_client else None
        existing_expiration = existing_client.get('expiredAt') if existing_client else None

        if not activation:
            if existing_activation and not force_update:
                activation = existing_activation
            else:
                activation = datetime.utcnow()

        if not expiration:
            if existing_expiration and not force_update:
                expiration = existing_expiration
            elif plan_duration:
                expiration = activation + timedelta(days=plan_duration)

        if activation and expiration and expiration < activation:
            return False, None, None, "Expiration date cannot be earlier than activation date."

        return True, activation, expiration, None
    
    @staticmethod
    def create(username, password, plan_id, template_id=None, status='active',
               plan_activation_date=None, plan_expiration_date=None):
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

            expiration_date = None
            plan_activation = None

            if plan_object_id:
                success, plan_activation, expiration_date, message = Client._prepare_plan_dates(
                    plan_object_id,
                    activation_input=plan_activation_date,
                    expiration_input=plan_expiration_date,
                    existing_client=None,
                    force_update=True
                )
                if not success:
                    return False, message

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
            
            plan_activation_input = data.pop('plan_activation_date', None)
            plan_expiration_input = data.pop('plan_expiration_date', None)

            # Convert plan_id to ObjectId if provided and update expiration
            if 'plan_id' in data:
                if data['plan_id']:
                    plan_object_id = data['plan_id']
                    if not isinstance(plan_object_id, ObjectId):
                        plan_object_id = ObjectId(plan_object_id)

                    plan_changed = existing_client.get('plan_id') != plan_object_id
                    force_update = plan_changed or not existing_client.get('planActivatedAt') or \
                        bool(plan_activation_input) or bool(plan_expiration_input)

                    success, plan_activation, expiration_date, message = Client._prepare_plan_dates(
                        plan_object_id,
                        activation_input=plan_activation_input,
                        expiration_input=plan_expiration_input,
                        existing_client=existing_client,
                        force_update=force_update
                    )
                    if not success:
                        return False, message

                    data['plan_id'] = plan_object_id
                    data['planActivatedAt'] = plan_activation
                    data['expiredAt'] = expiration_date
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