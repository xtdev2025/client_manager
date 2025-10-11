"""
Swagger/OpenAPI Configuration
Configures and initializes API documentation for the Client Manager application
"""
from typing import Dict, Any
from flask import Flask, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin


def create_apispec() -> APISpec:
    """
    Create APISpec instance with application metadata.
    
    Returns:
        APISpec: Configured APISpec instance
    """
    spec = APISpec(
        title="Client Manager API",
        version="1.0.0",
        openapi_version="3.0.3",
        info={
            "description": "API documentation for Client Manager - Sistema de Gerenciamento de Clientes",
            "contact": {
                "name": "API Support",
                "email": "support@clientmanager.com"
            },
            "license": {
                "name": "MIT",
                "url": "https://opensource.org/licenses/MIT"
            }
        },
        servers=[
            {
                "url": "http://localhost:5000",
                "description": "Development server"
            }
        ],
        plugins=[FlaskPlugin(), MarshmallowPlugin()],
        tags=[
            {"name": "Main", "description": "Main application routes"},
            {"name": "Auth", "description": "Authentication and authorization"},
            {"name": "Clients", "description": "Client management (admin area)"},
            {"name": "Client Portal", "description": "Client self-service area (my-* routes)"},
            {"name": "Admins", "description": "Administrator management"},
            {"name": "Plans", "description": "Subscription plan management"},
            {"name": "Domains", "description": "Domain management"},
            {"name": "Templates", "description": "Template management"},
            {"name": "Infos", "description": "Banking information management"},
            {"name": "Audit", "description": "Audit logs and system monitoring"}
        ]
    )
    
    # Add security scheme for session-based authentication
    spec.components.security_scheme(
        "session_auth",
        {
            "type": "apiKey",
            "in": "cookie",
            "name": "session",
            "description": "Session-based authentication using Flask sessions"
        }
    )
    
    # Add common response schemas
    _add_common_schemas(spec)
    
    return spec


def _add_common_schemas(spec: APISpec) -> None:
    """
    Add common response schemas to the specification.
    
    Args:
        spec: APISpec instance to add schemas to
    """
    # Note: ErrorResponse, ValidationError, and SuccessResponse schemas
    # are now registered automatically via Pydantic schemas in _document_routes()
    # to avoid duplication warnings
    
    # Pagination schema
    spec.components.schema(
        "PaginationInfo",
        {
            "type": "object",
            "properties": {
                "page": {"type": "integer", "description": "Current page number"},
                "per_page": {"type": "integer", "description": "Items per page"},
                "total": {"type": "integer", "description": "Total number of items"},
                "pages": {"type": "integer", "description": "Total number of pages"}
            }
        }
    )


def init_swagger(app: Flask) -> None:
    """
    Initialize Swagger UI and API documentation.
    
    Args:
        app: Flask application instance
    """
    # Create APISpec instance
    spec = create_apispec()
    
    # Configure Swagger UI
    SWAGGER_URL = '/api/docs'
    API_URL = '/api/swagger.json'
    
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "Client Manager API",
            'docExpansion': 'list',
            'defaultModelsExpandDepth': 3,
            'displayRequestDuration': True,
            'filter': True,
            'showExtensions': True,
            'showCommonExtensions': True,
            'tryItOutEnabled': True
        }
    )
    
    # Register Swagger UI blueprint
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    
    # Add route to serve OpenAPI spec
    @app.route(API_URL)
    def swagger_json():
        """Serve OpenAPI specification as JSON"""
        return jsonify(spec.to_dict())
    
    # Document all routes automatically
    with app.app_context():
        _document_routes(app, spec)


def _document_routes(app: Flask, spec: APISpec) -> None:
    """
    Automatically document all Flask routes.
    
    Args:
        app: Flask application instance
        spec: APISpec instance
    """
    from app.api.route_docs import document_all_routes
    from app.api.schemas import (
        UserSchema, ClientSchema, AdminSchema, PlanSchema,
        DomainSchema, TemplateSchema, InfoSchema, AuditLogSchema,
        DashboardStatsSchema, LoginRequest, LoginResponse,
        SuccessResponse, ErrorResponse, ValidationError,
        ClientListResponse, AdminListResponse, PlanListResponse,
        DomainListResponse, TemplateListResponse, InfoListResponse,
        AuditLogListResponse
    )
    
    # Add Pydantic schemas to the spec
    schemas_to_add = [
        ('UserSchema', UserSchema),
        ('ClientSchema', ClientSchema),
        ('AdminSchema', AdminSchema),
        ('PlanSchema', PlanSchema),
        ('DomainSchema', DomainSchema),
        ('TemplateSchema', TemplateSchema),
        ('InfoSchema', InfoSchema),
        ('AuditLogSchema', AuditLogSchema),
        ('DashboardStatsSchema', DashboardStatsSchema),
        ('LoginRequest', LoginRequest),
        ('LoginResponse', LoginResponse),
        ('SuccessResponse', SuccessResponse),
        ('ErrorResponse', ErrorResponse),
        ('ValidationError', ValidationError),
        ('ClientListResponse', ClientListResponse),
        ('AdminListResponse', AdminListResponse),
        ('PlanListResponse', PlanListResponse),
        ('DomainListResponse', DomainListResponse),
        ('TemplateListResponse', TemplateListResponse),
        ('InfoListResponse', InfoListResponse),
        ('AuditLogListResponse', AuditLogListResponse)
    ]
    
    for schema_name, schema_class in schemas_to_add:
        try:
            schema_dict = schema_class.model_json_schema()
            spec.components.schema(schema_name, schema_dict)
        except Exception as e:
            app.logger.warning(f"Failed to add schema {schema_name}: {e}")
    
    # Document all routes
    document_all_routes(spec)


def get_spec() -> Dict[str, Any]:
    """
    Get the OpenAPI specification as a dictionary.
    
    Returns:
        Dict containing the OpenAPI specification
    """
    spec = create_apispec()
    return spec.to_dict()
