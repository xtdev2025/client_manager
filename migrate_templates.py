#!/usr/bin/env python3
"""
Migration script to update existing templates with new structure.
This adds header, footer, versions, and pages fields to templates that don't have them.
"""

from app import create_app, mongo
from datetime import datetime

def migrate_templates():
    """Migrate existing templates to new structure"""
    app = create_app()
    
    with app.app_context():
        # Find all templates that don't have the new structure
        templates_to_update = mongo.db.templates.find({
            '$or': [
                {'header': {'$exists': False}},
                {'footer': {'$exists': False}},
                {'versions': {'$exists': False}},
                {'pages': {'$exists': False}}
            ]
        })
        
        count = 0
        for template in templates_to_update:
            update_data = {}
            
            # Add header if missing
            if 'header' not in template:
                update_data['header'] = {
                    'enabled': False,
                    'content': '',
                    'logo': '',
                    'backgroundColor': '#ffffff'
                }
            
            # Add footer if missing
            if 'footer' not in template:
                update_data['footer'] = {
                    'enabled': False,
                    'content': '',
                    'backgroundColor': '#f8f9fa'
                }
            
            # Add versions if missing
            if 'versions' not in template:
                update_data['versions'] = {
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
                }
            
            # Add pages if missing
            if 'pages' not in template:
                update_data['pages'] = [
                    {
                        'id': 'home',
                        'name': 'Home',
                        'type': 'home',
                        'required': True,
                        'content': ''
                    },
                    {
                        'id': 'splashscreen',
                        'name': 'Splashscreen',
                        'type': 'splashscreen',
                        'required': True,
                        'duration': 3000,
                        'content': ''
                    }
                ]
            
            # Update timestamp
            update_data['updatedAt'] = datetime.utcnow()
            
            # Perform update
            if update_data:
                result = mongo.db.templates.update_one(
                    {'_id': template['_id']},
                    {'$set': update_data}
                )
                if result.modified_count > 0:
                    count += 1
                    print(f"✓ Updated template: {template.get('name', 'Unknown')}")
        
        print(f"\n✅ Migration completed: {count} template(s) updated")

if __name__ == '__main__':
    print("Starting template migration...\n")
    migrate_templates()
