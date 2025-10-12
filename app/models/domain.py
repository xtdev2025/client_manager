from datetime import datetime

from bson.objectid import ObjectId
from flask import current_app

from app import mongo


class Domain:
    """Domain model for managing client domains"""

    @staticmethod
    def create(name, **kwargs):
        """Create a new domain"""
        try:
            # Default values
            defaults = {
                "cloudflare_api": None,
                "cloudflare_email": None,
                "cloudflare_password": None,
                "cloudflare_status": False,
                "ssl": False,
                "domain_limit": 5,
            }
            
            # Create domain object
            new_domain = {
                "name": name,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow(),
                **{**defaults, **kwargs}
            }

            # Insert into database
            result = mongo.db.domains.insert_one(new_domain)

            if result.inserted_id:
                return True, str(result.inserted_id)
            return False, "Database error"

        except Exception as e:
            current_app.logger.error(f"Error creating domain: {e}")
            return False, str(e)

    @staticmethod
    def update(domain_id, data):
        """Update domain information"""
        try:
            if isinstance(domain_id, str):
                domain_id = ObjectId(domain_id)

            # Handle boolean fields
            if "cloudflare_status" in data:
                data["cloudflare_status"] = bool(data["cloudflare_status"])
            if "ssl" in data:
                data["ssl"] = bool(data["ssl"])
            if "domain_limit" in data:
                data["domain_limit"] = int(data["domain_limit"])

            # Add updated timestamp
            data["updatedAt"] = datetime.utcnow()

            result = mongo.db.domains.update_one({"_id": domain_id}, {"$set": data})

            if result.modified_count > 0:
                return True, "Domain updated successfully"
            return False, "No changes made or domain not found"

        except Exception as e:
            current_app.logger.error(f"Error updating domain: {e}")
            return False, str(e)

    @staticmethod
    def delete(domain_id):
        """Delete domain"""
        try:
            if isinstance(domain_id, str):
                domain_id = ObjectId(domain_id)

            # Check if domain is associated with any clients
            client_count = mongo.db.client_domains.count_documents({"domain_id": domain_id})
            if client_count > 0:
                return False, f"Cannot delete domain: {client_count} clients are using this domain"

            result = mongo.db.domains.delete_one({"_id": domain_id})

            if result.deleted_count > 0:
                return True, "Domain deleted successfully"
            return False, "Domain not found"

        except Exception as e:
            current_app.logger.error(f"Error deleting domain: {e}")
            return False, str(e)

    @staticmethod
    def get_all():
        """Get all domains"""
        try:
            domains = list(mongo.db.domains.find())
            return domains
        except Exception as e:
            current_app.logger.error(f"Error getting domains: {e}")
            return []

    @staticmethod
    def get_by_id(domain_id):
        """Get domain by ID"""
        try:
            if isinstance(domain_id, str):
                domain_id = ObjectId(domain_id)

            domain = mongo.db.domains.find_one({"_id": domain_id})
            return domain
        except Exception as e:
            current_app.logger.error(f"Error getting domain by ID: {e}")
            return None

    @staticmethod
    def get_by_name(name):
        """Get domain by name"""
        try:
            domain = mongo.db.domains.find_one({"name": name})
            return domain
        except Exception as e:
            current_app.logger.error(f"Error getting domain by name: {e}")
            return None

    @staticmethod
    def assign_to_client(client_id, domain_id, subdomain):
        """Assign domain to client"""
        try:
            if isinstance(client_id, str):
                client_id = ObjectId(client_id)
            if isinstance(domain_id, str):
                domain_id = ObjectId(domain_id)

            # Check if the client already has this domain assigned
            existing = mongo.db.client_domains.find_one(
                {"client_id": client_id, "domain_id": domain_id, "subdomain": subdomain}
            )

            if existing:
                return False, "This domain is already assigned to the client"

            # Check if the client has reached the domain limit
            domain = Domain.get_by_id(domain_id)
            if not domain:
                return False, "Domain not found"

            client_domains_count = mongo.db.client_domains.count_documents({"client_id": client_id})
            if client_domains_count >= domain.get("domain_limit", 5):
                return (
                    False,
                    f"Client has reached the domain limit of {domain.get('domain_limit', 5)}",
                )

            # Create client-domain relationship
            new_client_domain = {
                "client_id": client_id,
                "domain_id": domain_id,
                "subdomain": subdomain,
                "full_domain": f"{subdomain}.{domain['name']}",
                "createdAt": datetime.utcnow(),
            }

            # If Cloudflare is enabled, we would add code here to create the DNS record via API
            if domain.get("cloudflare_status", False):
                # This would be where Cloudflare API integration goes
                # For now, just set a flag indicating it should be created
                new_client_domain["cloudflare_created"] = False

            result = mongo.db.client_domains.insert_one(new_client_domain)

            if result.inserted_id:
                return True, str(result.inserted_id)
            return False, "Database error"

        except Exception as e:
            current_app.logger.error(f"Error assigning domain to client: {e}")
            return False, str(e)

    @staticmethod
    def remove_from_client(client_id, client_domain_id):
        """Remove domain from client"""
        try:
            if isinstance(client_id, str):
                client_id = ObjectId(client_id)
            if isinstance(client_domain_id, str):
                client_domain_id = ObjectId(client_domain_id)

            # Get the client domain record first for potential Cloudflare cleanup
            client_domain = mongo.db.client_domains.find_one(
                {"_id": client_domain_id, "client_id": client_id}
            )

            if not client_domain:
                return False, "Domain assignment not found"

            # If Cloudflare was used, we would need to clean up DNS records
            if client_domain.get("cloudflare_created", False):
                # Cloudflare API integration for cleanup would go here
                pass

            result = mongo.db.client_domains.delete_one(
                {"_id": client_domain_id, "client_id": client_id}
            )

            if result.deleted_count > 0:
                return True, "Domain removed from client successfully"
            return False, "Domain assignment not found"

        except Exception as e:
            current_app.logger.error(f"Error removing domain from client: {e}")
            return False, str(e)

    @staticmethod
    def get_client_domains(client_id):
        """Get all domains assigned to a client"""
        try:
            if isinstance(client_id, str):
                client_id = ObjectId(client_id)

            client_domains = list(mongo.db.client_domains.find({"client_id": client_id}))

            # Enrich with domain details
            for cd in client_domains:
                if "domain_id" in cd:
                    domain = Domain.get_by_id(cd["domain_id"])
                    if domain:
                        cd["domain"] = domain

            return client_domains
        except Exception as e:
            current_app.logger.error(f"Error getting client domains: {e}")
            return []
