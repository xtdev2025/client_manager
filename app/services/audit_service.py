"""
Audit service for logging sensitive operations.
"""
from typing import Optional, Dict, Any
from datetime import datetime
from flask import request
from flask_login import current_user
from app import mongo


class AuditService:
    """Service class for audit logging operations"""

    @staticmethod
    def log_action(
        action: str, entity_type: str, entity_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None, user_id: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> bool:
        """
        Log a sensitive action in the audit trail.

        Args:
            action: The action performed (create, update, delete, etc.)
            entity_type: The type of entity (admin, client, plan, domain, etc.)
            entity_id: Optional ID of the entity affected
            details: Optional dict with additional details
            user_id: Optional user ID (uses current_user if not provided)
            ip_address: Optional IP address (uses request.remote_addr if not provided)

        Returns:
            bool indicating if logging succeeded
        """
        try:
            if user_id is None and current_user.is_authenticated:
                user_id = str(current_user.id)

            if ip_address is None:
                ip_address = request.remote_addr if request else 'unknown'

            user_agent = 'Unknown'
            if request:
                user_agent = request.headers.get('User-Agent', 'Unknown')

            audit_entry = {
                'action': action,
                'entity_type': entity_type,
                'entity_id': entity_id,
                'user_id': user_id,
                'ip_address': ip_address,
                'user_agent': user_agent,
                'timestamp': datetime.utcnow(),
                'details': details or {}
            }

            mongo.db.audit_logs.insert_one(audit_entry)
            return True

        except Exception as e:
            # Log error but don't fail the operation
            from flask import current_app
            current_app.logger.error(f"Error logging audit entry: {e}")
            return False

    @staticmethod
    def log_admin_action(
        action: str, admin_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Log an admin-related action.

        Args:
            action: The action performed
            admin_id: The admin ID affected
            details: Optional additional details

        Returns:
            bool indicating if logging succeeded
        """
        return AuditService.log_action(
            action=action,
            entity_type='admin',
            entity_id=admin_id,
            details=details
        )

    @staticmethod
    def log_client_action(
        action: str, client_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Log a client-related action.

        Args:
            action: The action performed
            client_id: The client ID affected
            details: Optional additional details

        Returns:
            bool indicating if logging succeeded
        """
        return AuditService.log_action(
            action=action,
            entity_type='client',
            entity_id=client_id,
            details=details
        )

    @staticmethod
    def log_plan_action(
        action: str, plan_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Log a plan-related action.

        Args:
            action: The action performed
            plan_id: The plan ID affected
            details: Optional additional details

        Returns:
            bool indicating if logging succeeded
        """
        return AuditService.log_action(
            action=action,
            entity_type='plan',
            entity_id=plan_id,
            details=details
        )

    @staticmethod
    def log_domain_action(
        action: str, domain_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Log a domain-related action.

        Args:
            action: The action performed
            domain_id: The domain ID affected
            details: Optional additional details

        Returns:
            bool indicating if logging succeeded
        """
        return AuditService.log_action(
            action=action,
            entity_type='domain',
            entity_id=domain_id,
            details=details
        )

    @staticmethod
    def log_template_action(
        action: str, template_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Log a template-related action.

        Args:
            action: The action performed
            template_id: The template ID affected
            details: Optional additional details

        Returns:
            bool indicating if logging succeeded
        """
        return AuditService.log_action(
            action=action,
            entity_type='template',
            entity_id=template_id,
            details=details
        )

    @staticmethod
    def log_info_action(
        action: str, info_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Log an info-related action.

        Args:
            action: The action performed
            info_id: The info ID affected
            details: Optional additional details

        Returns:
            bool indicating if logging succeeded
        """
        return AuditService.log_action(
            action=action,
            entity_type='info',
            entity_id=info_id,
            details=details
        )

    @staticmethod
    def get_recent_logs(
        limit: int = 100, entity_type: Optional[str] = None,
        user_id: Optional[str] = None, action: Optional[str] = None,
        start_date: Optional[datetime] = None, end_date: Optional[datetime] = None,
        page: int = 1
    ):
        """
        Get recent audit logs with optional filtering and pagination.

        Args:
            limit: Maximum number of logs to return per page
            entity_type: Optional filter by entity type
            user_id: Optional filter by user ID
            action: Optional filter by action type
            start_date: Optional filter by start date
            end_date: Optional filter by end date
            page: Page number for pagination (1-indexed)

        Returns:
            Tuple of (list of audit log entries, total count)
        """
        try:
            query = {}
            if entity_type:
                query['entity_type'] = entity_type
            if user_id:
                query['user_id'] = user_id
            if action:
                query['action'] = action

            # Date range filter
            if start_date or end_date:
                query['timestamp'] = {}
                if start_date:
                    query['timestamp']['$gte'] = start_date
                if end_date:
                    query['timestamp']['$lte'] = end_date

            # Get total count
            total = mongo.db.audit_logs.count_documents(query)

            # Calculate skip for pagination
            skip = (page - 1) * limit

            # Get logs with pagination
            logs = mongo.db.audit_logs.find(query).sort(
                'timestamp', -1
            ).skip(skip).limit(limit)

            return list(logs), total

        except Exception as e:
            from flask import current_app
            current_app.logger.error(f"Error retrieving audit logs: {e}")
            return [], 0
