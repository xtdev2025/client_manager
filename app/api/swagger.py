"""
Swagger/OpenAPI Configuration

This module configures Swagger UI and OpenAPI documentation for the
client_manager Flask application.

TODO: Implement the following features per issue #6:
- [ ] Configure flask-swagger-ui
- [ ] Set up apispec for OpenAPI 3.0 specification
- [ ] Document all 45+ endpoints with proper schemas
- [ ] Add authentication support (Bearer Token)
- [ ] Organize endpoints by tags (Auth, Clients, Admins, etc.)
- [ ] Add request/response examples
- [ ] Document all error responses (400, 401, 403, 404, 500)
"""


# TODO: Add swagger configuration
def init_swagger(app):
    """
    Initialize Swagger/OpenAPI documentation.

    Args:
        app: Flask application instance

    TODO:
    1. Install dependencies:
       - flask-swagger-ui==4.11.1
       - apispec==6.3.0
       - apispec-webframeworks==0.5.2

    2. Configure Swagger UI at /api/docs

    3. Generate OpenAPI spec from routes

    4. Add authentication to Swagger UI
    """
    pass


# API Documentation Tags
SWAGGER_TAGS = [
    {"name": "Auth", "description": "Autenticação e autorização de usuários"},
    {"name": "Main", "description": "Rotas principais da aplicação"},
    {"name": "Clients", "description": "Gerenciamento de clientes (área administrativa)"},
    {"name": "Client Portal", "description": "Área do cliente (rotas com padrão my-*)"},
    {"name": "Admins", "description": "Gerenciamento de administradores"},
    {"name": "Plans", "description": "Gerenciamento de planos"},
    {"name": "Domains", "description": "Gerenciamento de domínios"},
    {"name": "Templates", "description": "Gerenciamento de templates"},
    {"name": "Infos", "description": "Informações bancárias"},
    {"name": "Audit", "description": "Logs de auditoria"},
]


# Endpoint Documentation Checklist (45+ endpoints to document)
ENDPOINTS_TO_DOCUMENT = {
    "Main Routes": [
        "GET /",
        "GET /dashboard",
    ],
    "Auth Routes": [
        "GET/POST /auth/login",
        "GET /auth/logout",
        "GET/POST /auth/register",
        "GET/POST /auth/register_admin",
    ],
    "Client Routes": [
        "GET /clients/",
        "GET/POST /clients/create",
        "GET/POST /clients/edit/<client_id>",
        "POST /clients/delete/<client_id>",
        "GET /clients/view/<client_id>",
        "GET /clients/<client_id>/domains",
        "POST /clients/<client_id>/domains/add",
        "POST /clients/<client_id>/domains/remove/<client_domain_id>",
    ],
    "Client Portal Routes": [
        "GET /client/my-domains",
        "GET /client/my-click-stats",
        "GET /client/my-infos",
        "GET/POST /client/my-change-password",
    ],
    "Admin Routes": [
        "GET /admins/",
        "GET/POST /admins/create",
        "GET/POST /admins/edit/<admin_id>",
        "POST /admins/delete/<admin_id>",
        "GET/POST /admins/profile",
        "GET /admins/audit-logs",
        "POST /admins/clear-audit-logs",
    ],
    "Plan Routes": [
        "GET /plans/",
        "GET/POST /plans/create",
        "GET/POST /plans/edit/<plan_id>",
        "POST /plans/delete/<plan_id>",
        "GET /plans/view/<plan_id>",
    ],
    "Domain Routes": [
        "GET /domains/",
        "GET/POST /domains/create",
        "GET/POST /domains/edit/<domain_id>",
        "POST /domains/delete/<domain_id>",
        "GET /domains/view/<domain_id>",
    ],
    "Template Routes": [
        "GET /templates/",
        "GET/POST /templates/create",
        "GET/POST /templates/edit/<template_id>",
        "POST /templates/delete/<template_id>",
        "GET /templates/view/<template_id>",
    ],
    "Info Routes": [
        "GET /infos/",
        "GET /infos/client/<client_id>",
        "GET/POST /infos/create/<client_id>",
        "GET/POST /infos/edit/<info_id>",
        "GET /infos/view/<info_id>",
        "POST /infos/delete/<info_id>",
    ],
}
