import re
from datetime import datetime

from bson.objectid import ObjectId
from flask import current_app

from app import mongo


class Template:
    """Template model for client templates"""

    @staticmethod
    def generate_slug(name):
        """Generate URL-friendly slug from template name"""
        # Convert to lowercase and replace spaces with underscores
        slug = name.lower().strip()
        # Remove special characters, keep only alphanumeric, spaces, hyphens, and underscores
        slug = re.sub(r"[^a-z0-9\s\-_]", "", slug)
        # Replace spaces with underscores
        slug = re.sub(r"\s+", "_", slug)
        # Replace multiple underscores with single one
        slug = re.sub(r"_+", "_", slug)
        return slug

    @staticmethod
    def get_unique_slug(name):
        """Generates a unique slug, adding a suffix if necessary."""
        base_slug = Template.generate_slug(name)
        slug = base_slug
        
        existing = mongo.db.templates.find_one({"slug": slug})
        
        counter = 1
        while existing:
            slug = f"{base_slug}_{counter}"
            existing = mongo.db.templates.find_one({"slug": slug})
            counter += 1
            
        return slug


    @staticmethod
    def _assign_page_slugs(pages):
        """Ensure each page has a unique, URL-friendly slug."""
        if not pages:
            return pages

        normalized_pages = []
        seen_slugs = set()

        for index, page in enumerate(pages):
            page_data = page.copy()

            # Determine initial slug candidate
            candidate_sources = [page_data.get("slug"), page_data.get("id"), page_data.get("name"), f"pagina_{index + 1}"]
            candidate_slug = ""

            for source in candidate_sources:
                if source:
                    candidate_slug = Template.generate_slug(str(source))
                if candidate_slug:
                    break

            if not candidate_slug:
                candidate_slug = f"pagina_{index + 1}"

            base_slug = candidate_slug
            suffix = 2
            while candidate_slug in seen_slugs:
                candidate_slug = f"{base_slug}_{suffix}"
                suffix += 1

            page_data["slug"] = candidate_slug
            seen_slugs.add(candidate_slug)

            if not page_data.get("type") and "type" in page_data:
                page_data.pop("type", None)

            normalized_pages.append(page_data)

        return normalized_pages


    @staticmethod
    def create(name, description, content=None, status="active"):
        """Create a new template"""
        try:
            # Generate unique slug
            slug = Template.get_unique_slug(name)

            # Create template object with simplified structure
            new_template = {
                "name": name,
                "slug": slug,
                "description": description,
                "status": status,
                "pages": [
                    {
                        "id": "home",
                        "slug": "home",
                        "name": "Home",
                        "type": "home",
                        "content": "<h1>Bem-vindo</h1>",  # HTML personalizado
                        "order": 1,
                    }
                ],
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow(),
            }

            # Normalize page slugs before persisting
            new_template["pages"] = Template._assign_page_slugs(new_template.get("pages", []))

            # Insert into database
            result = mongo.db.templates.insert_one(new_template)

            if result.inserted_id:
                return True, str(result.inserted_id)
            return False, "Database error"

        except Exception as e:
            current_app.logger.error(f"Error creating template: {e}")
            return False, str(e)


    # ----------------------------------------------------------------------
    # NOVO MÉTODO PARA CLONAGEM
    # ----------------------------------------------------------------------
    @staticmethod
    def insert_from_dict(data: dict):
        """
        Insere um novo documento Template no banco de dados a partir de um dicionário,
        usado para clonagem. Requer que o campo '_id' já tenha sido removido.
        """
        try:
            # 1. Gera um novo slug único para o template clonado
            new_name = data.get('name', 'Template Clonado')
            data['slug'] = Template.get_unique_slug(new_name)
            
            # 2. Atualiza os timestamps de criação e atualização
            current_time = datetime.utcnow()
            data['createdAt'] = current_time
            data['updatedAt'] = current_time

            # 2b. Normaliza slugs das páginas clonadas
            data['pages'] = Template._assign_page_slugs(data.get('pages', []))

            # 3. Insere o documento completo (que inclui 'pages', 'versions', etc.)
            result = mongo.db.templates.insert_one(data)
            
            if result.inserted_id:
                return True, str(result.inserted_id)
            return False, "Database error during clone insertion"

        except Exception as e:
            current_app.logger.error(f"Error inserting template from dict (cloning): {e}")
            return False, str(e)
    # ----------------------------------------------------------------------


    @staticmethod
    def update(template_id, data):
        """Update template information"""
        try:
            if isinstance(template_id, str):
                template_id = ObjectId(template_id)

            # Add updated timestamp
            data["updatedAt"] = datetime.utcnow()

            if "pages" in data:
                data["pages"] = Template._assign_page_slugs(data.get("pages", []))

            result = mongo.db.templates.update_one({"_id": template_id}, {"$set": data})

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

            result = mongo.db.templates.delete_one({"_id": template_id})

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
            for template in templates:
                if template.get("pages"):
                    template["pages"] = Template._assign_page_slugs(template.get("pages", []))
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

            template = mongo.db.templates.find_one({"_id": template_id})
            if template and template.get("pages"):
                template["pages"] = Template._assign_page_slugs(template.get("pages", []))
            return template
        except Exception as e:
            current_app.logger.error(f"Error getting template by ID: {e}")
            return None

    @staticmethod
    def get_by_slug(slug):
        """Get template by slug"""
        try:
            template = mongo.db.templates.find_one({"slug": slug})
            if template and template.get("pages"):
                template["pages"] = Template._assign_page_slugs(template.get("pages", []))
            return template
        except Exception as e:
            current_app.logger.error(f"Error getting template by slug: {e}")
            return None

    @staticmethod
    def get_page_by_id(slug, page_id):
        """Get a specific page from a template by slug and page identifier (ID or slug)."""
        try:
            template = Template.get_by_slug(slug)
            if not template:
                return None

            # Find the page with matching ID
            for page in template.get("pages", []):
                page_slug = page.get("slug")
                if page.get("id") == page_id:
                    return page
                if page_slug and page_slug == page_id:
                    return page

                # Fallback: derive slug from name or id
                generated_slug = Template.generate_slug(page.get("name", ""))
                if generated_slug == page_id:
                    return page

            return None
        except Exception as e:
            current_app.logger.error(f"Error getting page: {e}")
            return None

    @staticmethod
    def get_page_by_slug(slug, page_slug):
        """Alias for get_page_by_id using page slug explicitly."""
        return Template.get_page_by_id(slug, page_slug)