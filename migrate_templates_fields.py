#!/usr/bin/env python3
"""
Migration script to add slug field and convert pages structure
from content-based to fields-based system
"""

from app import create_app, mongo
from datetime import datetime
import re

def generate_slug(name):
    """Generate URL-friendly slug from template name"""
    slug = name.lower().strip()
    slug = re.sub(r'[^a-z0-9\s\-_]', '', slug)
    slug = re.sub(r'\s+', '_', slug)
    slug = re.sub(r'_+', '_', slug)
    return slug

def migrate_templates():
    """Add slug and convert page structure for all templates"""
    
    app = create_app()
    
    with app.app_context():
        print("Starting template migration...")
        print("-" * 50)
        
        # Get all templates
        templates = list(mongo.db.templates.find())
        print(f"Found {len(templates)} templates to migrate\n")
        
        updated_count = 0
        skipped_count = 0
        
        for template in templates:
            template_name = template.get('name', 'Unknown')
            template_id = template['_id']
            needs_update = False
            update_data = {}
            
            print(f"Processing: {template_name} ({template_id})")
            
            # 1. Add slug if missing
            if 'slug' not in template:
                slug = generate_slug(template_name)
                
                # Check for duplicate slugs
                existing = mongo.db.templates.find_one({'slug': slug, '_id': {'$ne': template_id}})
                if existing:
                    counter = 1
                    while existing:
                        test_slug = f"{slug}_{counter}"
                        existing = mongo.db.templates.find_one({'slug': test_slug, '_id': {'$ne': template_id}})
                        counter += 1
                    slug = test_slug
                
                update_data['slug'] = slug
                needs_update = True
                print(f"  ✓ Added slug: {slug}")
            else:
                print(f"  - Slug already exists: {template.get('slug')}")
            
            # 2. Convert pages structure from content to fields
            pages = template.get('pages', [])
            if pages:
                converted_pages = []
                pages_converted = False
                
                for page in pages:
                    # Check if page still uses old 'content' field
                    if 'content' in page and 'fields' not in page:
                        # Convert old structure to new structure
                        new_page = {
                            'id': page.get('id', ''),
                            'name': page.get('name', ''),
                            'type': page.get('type', 'custom'),
                            'required': page.get('required', False),
                            'fields': []  # Empty fields list - admin will configure
                        }
                        
                        # Preserve duration for splashscreen
                        if 'duration' in page:
                            new_page['duration'] = page['duration']
                        
                        # Preserve loginTypes if present
                        if 'loginTypes' in page:
                            new_page['loginTypes'] = page['loginTypes']
                        
                        converted_pages.append(new_page)
                        pages_converted = True
                        print(f"  ✓ Converted page: {page.get('name')} (content → fields)")
                    else:
                        # Page already has new structure or needs no conversion
                        if 'fields' in page:
                            print(f"  - Page already has fields structure: {page.get('name')}")
                        converted_pages.append(page)
                
                if pages_converted:
                    update_data['pages'] = converted_pages
                    needs_update = True
            
            # 3. Update the template if needed
            if needs_update:
                update_data['updatedAt'] = datetime.utcnow()
                
                result = mongo.db.templates.update_one(
                    {'_id': template_id},
                    {'$set': update_data}
                )
                
                if result.modified_count > 0:
                    updated_count += 1
                    print(f"  ✓ Template updated successfully\n")
                else:
                    print(f"  ! Update failed\n")
            else:
                skipped_count += 1
                print(f"  - No changes needed\n")
        
        print("-" * 50)
        print(f"Migration complete!")
        print(f"Updated: {updated_count}")
        print(f"Skipped: {skipped_count}")
        print(f"Total: {len(templates)}")

if __name__ == '__main__':
    migrate_templates()
