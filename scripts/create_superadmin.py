#!/usr/bin/env python3
"""
Script to create a super_admin user manually
Usage: python create_superadmin.py <username> <password>
"""

import sys
import os

# Add the parent directory to the path so we can import from app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask
from app import create_app, mongo, bcrypt
from datetime import datetime

def create_super_admin(username, password):
    """Create a super_admin user with the specified username and password"""
    app = create_app()
    
    with app.app_context():
        # Check if the username already exists
        existing_user = mongo.db.admins.find_one({'username': username})
        if existing_user:
            print(f"Error: User '{username}' already exists.")
            return False
            
        # Hash the password
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Create the admin document
        new_admin = {
            'username': username,
            'password': hashed_pw,
            'role': 'super_admin',
            'createdAt': datetime.utcnow(),
            'updatedAt': datetime.utcnow(),
        }
        
        # Insert into database
        result = mongo.db.admins.insert_one(new_admin)
        
        if result.inserted_id:
            print(f"Super admin '{username}' created successfully!")
            return True
        else:
            print("Failed to create super admin.")
            return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python create_superadmin.py <username> <password>")
        sys.exit(1)
        
    username = sys.argv[1]
    password = sys.argv[2]
    
    success = create_super_admin(username, password)
    sys.exit(0 if success else 1)