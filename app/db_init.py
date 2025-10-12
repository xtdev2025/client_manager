from datetime import datetime

from bson.objectid import ObjectId

from app import bcrypt, mongo


def initialize_db():
    """
    Initialize database with default data if it's empty.
    This includes:
    1. Creating a super_admin user if no admin exists
    2. Creating 3 default plans if no plans exist
    3. Creating default templates if no templates exist
    """
    # Check if there are any admins
    if mongo.db.admins.count_documents({}) == 0:
        create_default_admin()

    # Check if there are any plans
    if mongo.db.plans.count_documents({}) == 0:
        create_default_plans()

    # Check if there are any templates
    if mongo.db.templates.count_documents({}) == 0:
        create_default_templates()


def create_default_admin():
    """Create the default super_admin user"""
    try:
        # Default credentials (should be changed after first login)
        username = "superadmin"
        password = "Admin@123"  # This should be changed immediately

        # Hash the password
        hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")

        # Create the admin document
        new_admin = {
            "username": username,
            "password": hashed_pw,
            "role": "super_admin",
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
        }

        # Insert into database
        result = mongo.db.admins.insert_one(new_admin)

        if result.inserted_id:
            print(f"Default super_admin created with username: {username}")
        else:
            print("Failed to create default super_admin")

    except Exception as e:
        print(f"Error creating default admin: {e}")


def create_default_plans():
    """Create 3 default subscription plans"""
    try:
        # Define the three default plans
        default_plans = [
            {
                "name": "Basic Plan",
                "description": "Basic features for small businesses",
                "price": 29.99,
                "duration_days": 30,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow(),
            },
            {
                "name": "Standard Plan",
                "description": "Standard features for growing businesses",
                "price": 59.99,
                "duration_days": 30,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow(),
            },
            {
                "name": "Premium Plan",
                "description": "Premium features for established businesses",
                "price": 99.99,
                "duration_days": 30,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow(),
            },
        ]

        # Insert all plans
        result = mongo.db.plans.insert_many(default_plans)

        if result.inserted_ids:
            print(f"Created {len(result.inserted_ids)} default plans")
        else:
            print("Failed to create default plans")

    except Exception as e:
        print(f"Error creating default plans: {e}")


def create_default_templates():
    """Create default templates"""
    try:
        # Define the default templates
        default_templates = [
            {
                "name": "Basic Template",
                "description": "A simple template for basic websites",
                "content": '{"header": true, "footer": true, "sidebar": false}',
                "status": "active",
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow(),
            },
            {
                "name": "Professional Template",
                "description": "A professional template for business websites",
                "content": '{"header": true, "footer": true, "sidebar": true, "gallery": true}',
                "status": "active",
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow(),
            },
            {
                "name": "E-commerce Template",
                "description": "Template optimized for online stores",
                "content": '{"header": true, "footer": true, "sidebar": true, "cart": true, "product_display": true}',
                "status": "active",
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow(),
            },
        ]

        # Insert all templates
        result = mongo.db.templates.insert_many(default_templates)

        if result.inserted_ids:
            print(f"Created {len(result.inserted_ids)} default templates")
        else:
            print("Failed to create default templates")

    except Exception as e:
        print(f"Error creating default templates: {e}")
