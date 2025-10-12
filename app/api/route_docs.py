"""
Route Documentation Helpers
Functions to document Flask routes with OpenAPI specifications
"""
from typing import Any, Dict

from apispec import APISpec


def add_path(spec: APISpec, path: str, operations: Dict[str, Any]) -> None:
    """
    Add a path with operations to the spec.

    Args:
        spec: APISpec instance
        path: URL path
        operations: Dictionary of HTTP methods and their operations
    """
    # Access internal _paths dict directly
    if not hasattr(spec, "_paths"):
        spec._paths = {}
    spec._paths[path] = operations


def document_main_routes(spec: APISpec) -> None:
    """Document main application routes."""

    # GET / - Home page
    add_path(
        spec,
        "/",
        {
            "get": {
                "tags": ["Main"],
                "summary": "Home page",
                "description": "Renders the home page. Redirects to dashboard if user is authenticated.",
                "responses": {
                    "200": {
                        "description": "Home page rendered successfully",
                        "content": {"text/html": {"schema": {"type": "string"}}},
                    },
                    "302": {"description": "Redirect to dashboard if authenticated"},
                },
            }
        },
    )

    # GET /dashboard - Dashboard
    add_path(
        spec,
        "/dashboard",
        {
            "get": {
                "tags": ["Main"],
                "summary": "User dashboard",
                "description": "Displays dashboard with different content for admin and client users. Requires authentication.",
                "security": [{"session_auth": []}],
                "responses": {
                    "200": {
                        "description": "Dashboard rendered successfully",
                        "content": {
                            "text/html": {"schema": {"type": "string"}},
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/DashboardStatsSchema"}
                            },
                        },
                    },
                    "401": {
                        "description": "Unauthorized - User not logged in",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                            }
                        },
                    },
                },
            }
        },
    )


def document_auth_routes(spec: APISpec) -> None:
    """Document authentication routes."""

    # GET/POST /auth/login
    add_path(
        spec,
        "/auth/login",
        {
            "get": {
                "tags": ["Auth"],
                "summary": "Display login page",
                "description": "Renders the login page. Redirects to home if already authenticated.",
                "responses": {
                    "200": {
                        "description": "Login page rendered successfully",
                        "content": {"text/html": {"schema": {"type": "string"}}},
                    },
                    "302": {"description": "Redirect to home if already authenticated"},
                },
            },
            "post": {
                "tags": ["Auth"],
                "summary": "Process login",
                "description": "Authenticates user credentials and creates session. Rate limited to 10 requests per minute.",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "username": {"type": "string", "description": "Username"},
                                    "password": {
                                        "type": "string",
                                        "format": "password",
                                        "description": "Password",
                                    },
                                },
                                "required": ["username", "password"],
                            }
                        }
                    },
                },
                "responses": {
                    "302": {"description": "Login successful, redirect to dashboard"},
                    "200": {"description": "Login failed, re-render login page with error"},
                    "429": {"description": "Too many requests - Rate limit exceeded"},
                },
            },
        },
    )

    # GET /auth/logout
    add_path(
        spec,
        "/auth/logout",
        {
            "get": {
                "tags": ["Auth"],
                "summary": "Logout user",
                "description": "Logs out the current user and destroys session.",
                "security": [{"session_auth": []}],
                "responses": {
                    "302": {"description": "Logout successful, redirect to login page"},
                    "401": {"description": "Unauthorized - User not logged in"},
                },
            }
        },
    )

    # GET/POST /auth/register
    add_path(
        spec,
        "/auth/register",
        {
            "get": {
                "tags": ["Auth"],
                "summary": "Display registration page",
                "description": "Renders the client registration page.",
                "responses": {
                    "200": {"description": "Registration page rendered successfully"},
                    "302": {"description": "Redirect to home if already authenticated"},
                },
            },
            "post": {
                "tags": ["Auth"],
                "summary": "Register new client",
                "description": "Creates a new client account.",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "username": {"type": "string", "minLength": 3},
                                    "password": {
                                        "type": "string",
                                        "minLength": 6,
                                        "format": "password",
                                    },
                                    "confirm_password": {
                                        "type": "string",
                                        "minLength": 6,
                                        "format": "password",
                                    },
                                },
                                "required": ["username", "password", "confirm_password"],
                            }
                        }
                    },
                },
                "responses": {
                    "302": {"description": "Registration successful, redirect to login"},
                    "200": {"description": "Registration failed, re-render page with error"},
                    "400": {
                        "description": "Bad request - Validation error",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ValidationError"}
                            }
                        },
                    },
                },
            },
        },
    )

    # GET/POST /auth/register_admin
    add_path(
        spec,
        "/auth/register_admin",
        {
            "get": {
                "tags": ["Auth"],
                "summary": "Display admin registration page",
                "description": "Renders admin registration page. Only accessible by super_admin.",
                "security": [{"session_auth": []}],
                "responses": {
                    "200": {"description": "Admin registration page rendered"},
                    "401": {"description": "Unauthorized"},
                    "403": {"description": "Forbidden - Not a super_admin"},
                },
            },
            "post": {
                "tags": ["Auth"],
                "summary": "Register new admin",
                "description": "Creates a new admin account. Only super_admin can access. Rate limited to 5/min.",
                "security": [{"session_auth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "username": {"type": "string", "minLength": 3},
                                    "password": {
                                        "type": "string",
                                        "minLength": 6,
                                        "format": "password",
                                    },
                                    "confirm_password": {
                                        "type": "string",
                                        "minLength": 6,
                                        "format": "password",
                                    },
                                    "role": {"type": "string", "enum": ["admin", "super_admin"]},
                                },
                                "required": ["username", "password", "confirm_password"],
                            }
                        }
                    },
                },
                "responses": {
                    "302": {"description": "Registration successful"},
                    "401": {"description": "Unauthorized"},
                    "403": {"description": "Forbidden"},
                    "429": {"description": "Rate limit exceeded"},
                },
            },
        },
    )


def document_client_routes(spec: APISpec) -> None:
    """Document client management routes (admin area)."""

    # GET /clients/ - List clients
    add_path(
        spec,
        "/clients/",
        {
            "get": {
                "tags": ["Clients"],
                "summary": "List all clients",
                "description": "Retrieves list of all clients with their plan information. Admin access required.",
                "security": [{"session_auth": []}],
                "responses": {
                    "200": {
                        "description": "List of clients retrieved successfully",
                        "content": {
                            "text/html": {"schema": {"type": "string"}},
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ClientListResponse"}
                            },
                        },
                    },
                    "401": {"description": "Unauthorized"},
                    "403": {"description": "Forbidden - Admin access required"},
                },
            }
        },
    )

    # GET/POST /clients/create - Create client
    add_path(
        spec,
        "/clients/create",
        {
            "get": {
                "tags": ["Clients"],
                "summary": "Display client creation form",
                "description": "Renders form to create a new client. Admin access required.",
                "security": [{"session_auth": []}],
                "responses": {
                    "200": {"description": "Form rendered successfully"},
                    "401": {"description": "Unauthorized"},
                    "403": {"description": "Forbidden - Admin access required"},
                },
            },
            "post": {
                "tags": ["Clients"],
                "summary": "Create new client",
                "description": "Creates a new client with specified plan and template. Admin access required.",
                "security": [{"session_auth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "username": {"type": "string", "minLength": 3},
                                    "password": {
                                        "type": "string",
                                        "minLength": 6,
                                        "format": "password",
                                    },
                                    "plan_id": {
                                        "type": "string",
                                        "description": "MongoDB ObjectId of plan",
                                    },
                                    "template_id": {
                                        "type": "string",
                                        "description": "MongoDB ObjectId of template",
                                    },
                                    "status": {
                                        "type": "string",
                                        "enum": ["active", "inactive"],
                                        "default": "active",
                                    },
                                    "plan_activation_date": {
                                        "type": "string",
                                        "format": "date",
                                        "description": "Plan activation date (YYYY-MM-DD)",
                                    },
                                    "plan_expiration_date": {
                                        "type": "string",
                                        "format": "date",
                                        "description": "Plan expiration date (YYYY-MM-DD)",
                                    },
                                },
                                "required": ["username", "password"],
                            }
                        }
                    },
                },
                "responses": {
                    "302": {"description": "Client created successfully, redirect to list"},
                    "200": {"description": "Validation error, re-render form"},
                    "401": {"description": "Unauthorized"},
                    "403": {"description": "Forbidden"},
                },
            },
        },
    )

    # GET/POST /clients/edit/<client_id> - Edit client
    add_path(
        spec,
        "/clients/edit/{client_id}",
        {
            "get": {
                "tags": ["Clients"],
                "summary": "Display client edit form",
                "description": "Renders form to edit an existing client. Admin access required.",
                "security": [{"session_auth": []}],
                "parameters": [
                    {
                        "name": "client_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                        "description": "Client MongoDB ObjectId",
                    }
                ],
                "responses": {
                    "200": {"description": "Form rendered successfully"},
                    "404": {"description": "Client not found"},
                    "401": {"description": "Unauthorized"},
                    "403": {"description": "Forbidden"},
                },
            },
            "post": {
                "tags": ["Clients"],
                "summary": "Update client",
                "description": "Updates client information. Admin access required.",
                "security": [{"session_auth": []}],
                "parameters": [
                    {
                        "name": "client_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "username": {"type": "string"},
                                    "password": {
                                        "type": "string",
                                        "format": "password",
                                        "description": "Leave empty to keep current",
                                    },
                                    "plan_id": {"type": "string"},
                                    "template_id": {"type": "string"},
                                    "status": {"type": "string", "enum": ["active", "inactive"]},
                                    "plan_activation_date": {"type": "string", "format": "date"},
                                    "plan_expiration_date": {"type": "string", "format": "date"},
                                },
                            }
                        }
                    },
                },
                "responses": {
                    "302": {"description": "Client updated successfully"},
                    "200": {"description": "Validation error"},
                    "404": {"description": "Client not found"},
                    "401": {"description": "Unauthorized"},
                    "403": {"description": "Forbidden"},
                },
            },
        },
    )

    # POST /clients/delete/<client_id> - Delete client
    add_path(
        spec,
        "/clients/delete/{client_id}",
        {
            "post": {
                "tags": ["Clients"],
                "summary": "Delete client",
                "description": "Deletes a client permanently. Admin access required.",
                "security": [{"session_auth": []}],
                "parameters": [
                    {
                        "name": "client_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "responses": {
                    "302": {"description": "Client deleted successfully"},
                    "404": {"description": "Client not found"},
                    "401": {"description": "Unauthorized"},
                    "403": {"description": "Forbidden"},
                },
            }
        },
    )

    # GET /clients/view/<client_id> - View client details
    add_path(
        spec,
        "/clients/view/{client_id}",
        {
            "get": {
                "tags": ["Clients"],
                "summary": "View client details",
                "description": "Displays detailed information about a specific client. Admin access required.",
                "security": [{"session_auth": []}],
                "parameters": [
                    {
                        "name": "client_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Client details retrieved",
                        "content": {
                            "text/html": {"schema": {"type": "string"}},
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ClientSchema"}
                            },
                        },
                    },
                    "404": {"description": "Client not found"},
                    "401": {"description": "Unauthorized"},
                    "403": {"description": "Forbidden"},
                },
            }
        },
    )

    # GET /clients/<client_id>/domains - List client domains
    add_path(
        spec,
        "/clients/{client_id}/domains",
        {
            "get": {
                "tags": ["Clients"],
                "summary": "List client domains",
                "description": "Retrieves all domains associated with a client. Admin access required.",
                "security": [{"session_auth": []}],
                "parameters": [
                    {
                        "name": "client_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Domains retrieved successfully",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/DomainListResponse"}
                            }
                        },
                    },
                    "404": {"description": "Client not found"},
                    "401": {"description": "Unauthorized"},
                    "403": {"description": "Forbidden"},
                },
            }
        },
    )

    # POST /clients/<client_id>/domains/add - Add domain to client
    add_path(
        spec,
        "/clients/{client_id}/domains/add",
        {
            "post": {
                "tags": ["Clients"],
                "summary": "Add domain to client",
                "description": "Associates a domain with a client. Admin access required.",
                "security": [{"session_auth": []}],
                "parameters": [
                    {
                        "name": "client_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "domain_id": {
                                        "type": "string",
                                        "description": "Domain MongoDB ObjectId to associate",
                                    }
                                },
                                "required": ["domain_id"],
                            }
                        }
                    },
                },
                "responses": {
                    "302": {"description": "Domain added successfully"},
                    "400": {"description": "Invalid request"},
                    "404": {"description": "Client or domain not found"},
                    "401": {"description": "Unauthorized"},
                    "403": {"description": "Forbidden"},
                },
            }
        },
    )

    # POST /clients/<client_id>/domains/remove/<client_domain_id> - Remove domain
    add_path(
        spec,
        "/clients/{client_id}/domains/remove/{client_domain_id}",
        {
            "post": {
                "tags": ["Clients"],
                "summary": "Remove domain from client",
                "description": "Removes domain association from a client. Admin access required.",
                "security": [{"session_auth": []}],
                "parameters": [
                    {
                        "name": "client_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    },
                    {
                        "name": "client_domain_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    },
                ],
                "responses": {
                    "302": {"description": "Domain removed successfully"},
                    "404": {"description": "Client or domain association not found"},
                    "401": {"description": "Unauthorized"},
                    "403": {"description": "Forbidden"},
                },
            }
        },
    )


def document_all_routes(spec: APISpec) -> None:
    """Document all application routes."""
    document_main_routes(spec)
    document_auth_routes(spec)
    document_client_routes(spec)
    document_client_portal_routes(spec)
    document_admin_routes(spec)
    document_plan_routes(spec)
    document_domain_routes(spec)
    document_template_routes(spec)
    document_info_routes(spec)


def document_client_portal_routes(spec: APISpec) -> None:
    """Document client self-service portal routes."""

    # GET /client/my-domains
    add_path(
        spec,
        "/client/my-domains",
        {
            "get": {
                "tags": ["Client Portal"],
                "summary": "View my domains",
                "description": "Client views their own domains. Client access only.",
                "security": [{"session_auth": []}],
                "responses": {
                    "200": {
                        "description": "Domains retrieved successfully",
                        "content": {"text/html": {"schema": {"type": "string"}}},
                    },
                    "401": {"description": "Unauthorized"},
                    "403": {"description": "Forbidden - Client access only"},
                },
            }
        },
    )

    # GET /client/my-click-stats
    add_path(
        spec,
        "/client/my-click-stats",
        {
            "get": {
                "tags": ["Client Portal"],
                "summary": "View my click statistics",
                "description": "Client views click statistics for their domains. Client access only.",
                "security": [{"session_auth": []}],
                "responses": {
                    "200": {"description": "Statistics retrieved successfully"},
                    "401": {"description": "Unauthorized"},
                    "403": {"description": "Forbidden - Client access only"},
                },
            }
        },
    )

    # GET /client/my-infos
    add_path(
        spec,
        "/client/my-infos",
        {
            "get": {
                "tags": ["Client Portal"],
                "summary": "View my banking information",
                "description": "Client views their banking information. Client access only.",
                "security": [{"session_auth": []}],
                "responses": {
                    "200": {"description": "Banking info retrieved successfully"},
                    "401": {"description": "Unauthorized"},
                    "403": {"description": "Forbidden - Client access only"},
                },
            }
        },
    )

    # GET/POST /client/my-change-password
    add_path(
        spec,
        "/client/my-change-password",
        {
            "get": {
                "tags": ["Client Portal"],
                "summary": "Display password change form",
                "description": "Renders password change form. Client access only.",
                "security": [{"session_auth": []}],
                "responses": {
                    "200": {"description": "Form rendered"},
                    "401": {"description": "Unauthorized"},
                },
            },
            "post": {
                "tags": ["Client Portal"],
                "summary": "Change my password",
                "description": "Changes client's password. Client access only.",
                "security": [{"session_auth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "current_password": {"type": "string", "format": "password"},
                                    "new_password": {
                                        "type": "string",
                                        "minLength": 6,
                                        "format": "password",
                                    },
                                    "confirm_password": {
                                        "type": "string",
                                        "minLength": 6,
                                        "format": "password",
                                    },
                                },
                                "required": [
                                    "current_password",
                                    "new_password",
                                    "confirm_password",
                                ],
                            }
                        }
                    },
                },
                "responses": {
                    "302": {"description": "Password changed successfully"},
                    "200": {"description": "Validation error"},
                    "401": {"description": "Unauthorized"},
                },
            },
        },
    )


def document_admin_routes(spec: APISpec) -> None:
    """Document admin management routes."""

    # GET /admins/
    add_path(
        spec,
        "/admins/",
        {
            "get": {
                "tags": ["Admins"],
                "summary": "List all admins",
                "description": "Retrieves list of all administrators. Admin access required.",
                "security": [{"session_auth": []}],
                "responses": {
                    "200": {
                        "description": "Admins retrieved",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/AdminListResponse"}
                            }
                        },
                    },
                    "401": {"description": "Unauthorized"},
                    "403": {"description": "Forbidden"},
                },
            }
        },
    )

    # GET/POST /admins/create
    add_path(
        spec,
        "/admins/create",
        {
            "get": {
                "tags": ["Admins"],
                "summary": "Display admin creation form",
                "description": "Renders admin creation form. Super admin only.",
                "security": [{"session_auth": []}],
                "responses": {
                    "200": {"description": "Form rendered"},
                    "401": {"description": "Unauthorized"},
                    "403": {"description": "Forbidden - Super admin only"},
                },
            },
            "post": {
                "tags": ["Admins"],
                "summary": "Create new admin",
                "description": "Creates a new administrator. Super admin only.",
                "security": [{"session_auth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "username": {"type": "string", "minLength": 3},
                                    "password": {
                                        "type": "string",
                                        "minLength": 6,
                                        "format": "password",
                                    },
                                    "role": {"type": "string", "enum": ["admin", "super_admin"]},
                                },
                                "required": ["username", "password"],
                            }
                        }
                    },
                },
                "responses": {
                    "302": {"description": "Admin created"},
                    "200": {"description": "Validation error"},
                    "401": {"description": "Unauthorized"},
                    "403": {"description": "Forbidden"},
                },
            },
        },
    )

    # GET/POST /admins/edit/<admin_id>
    add_path(
        spec,
        "/admins/edit/{admin_id}",
        {
            "get": {
                "tags": ["Admins"],
                "summary": "Display admin edit form",
                "description": "Renders admin edit form. Super admin only.",
                "security": [{"session_auth": []}],
                "parameters": [
                    {
                        "name": "admin_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "responses": {
                    "200": {"description": "Form rendered"},
                    "404": {"description": "Admin not found"},
                    "401": {"description": "Unauthorized"},
                    "403": {"description": "Forbidden"},
                },
            },
            "post": {
                "tags": ["Admins"],
                "summary": "Update admin",
                "description": "Updates admin information. Super admin only.",
                "security": [{"session_auth": []}],
                "parameters": [
                    {
                        "name": "admin_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "username": {"type": "string"},
                                    "password": {
                                        "type": "string",
                                        "format": "password",
                                        "description": "Leave empty to keep current",
                                    },
                                    "role": {"type": "string", "enum": ["admin", "super_admin"]},
                                },
                            }
                        }
                    },
                },
                "responses": {
                    "302": {"description": "Admin updated"},
                    "404": {"description": "Admin not found"},
                    "401": {"description": "Unauthorized"},
                    "403": {"description": "Forbidden"},
                },
            },
        },
    )

    # POST /admins/delete/<admin_id>
    add_path(
        spec,
        "/admins/delete/{admin_id}",
        {
            "post": {
                "tags": ["Admins"],
                "summary": "Delete admin",
                "description": "Deletes an administrator. Super admin only.",
                "security": [{"session_auth": []}],
                "parameters": [
                    {
                        "name": "admin_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "responses": {
                    "302": {"description": "Admin deleted"},
                    "404": {"description": "Admin not found"},
                    "401": {"description": "Unauthorized"},
                    "403": {"description": "Forbidden"},
                },
            }
        },
    )

    # GET/POST /admins/profile
    add_path(
        spec,
        "/admins/profile",
        {
            "get": {
                "tags": ["Admins"],
                "summary": "View admin profile",
                "description": "Displays logged-in admin's profile. Admin access required.",
                "security": [{"session_auth": []}],
                "responses": {
                    "200": {"description": "Profile rendered"},
                    "401": {"description": "Unauthorized"},
                },
            },
            "post": {
                "tags": ["Admins"],
                "summary": "Update admin profile",
                "description": "Updates logged-in admin's profile. Admin access required.",
                "security": [{"session_auth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "username": {"type": "string"},
                                    "password": {"type": "string", "format": "password"},
                                },
                            }
                        }
                    },
                },
                "responses": {
                    "302": {"description": "Profile updated"},
                    "401": {"description": "Unauthorized"},
                },
            },
        },
    )

    # GET /admins/audit-logs
    add_path(
        spec,
        "/admins/audit-logs",
        {
            "get": {
                "tags": ["Audit"],
                "summary": "View audit logs",
                "description": "Displays system audit logs. Admin access required.",
                "security": [{"session_auth": []}],
                "responses": {
                    "200": {
                        "description": "Logs retrieved",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/AuditLogListResponse"}
                            }
                        },
                    },
                    "401": {"description": "Unauthorized"},
                    "403": {"description": "Forbidden"},
                },
            }
        },
    )

    # POST /admins/clear-audit-logs
    add_path(
        spec,
        "/admins/clear-audit-logs",
        {
            "post": {
                "tags": ["Audit"],
                "summary": "Clear audit logs",
                "description": "Clears all audit logs. Super admin only.",
                "security": [{"session_auth": []}],
                "responses": {
                    "302": {"description": "Logs cleared"},
                    "401": {"description": "Unauthorized"},
                    "403": {"description": "Forbidden - Super admin only"},
                },
            }
        },
    )


def document_plan_routes(spec: APISpec) -> None:
    """Document plan management routes."""

    # GET /plans/
    add_path(
        spec,
        "/plans/",
        {
            "get": {
                "tags": ["Plans"],
                "summary": "List all plans",
                "description": "Retrieves list of all subscription plans. Admin access required.",
                "security": [{"session_auth": []}],
                "responses": {
                    "200": {
                        "description": "Plans retrieved",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/PlanListResponse"}
                            }
                        },
                    },
                    "401": {"description": "Unauthorized"},
                    "403": {"description": "Forbidden"},
                },
            }
        },
    )

    # GET/POST /plans/create
    add_path(
        spec,
        "/plans/create",
        {
            "get": {
                "tags": ["Plans"],
                "summary": "Display plan creation form",
                "description": "Renders plan creation form. Admin access required.",
                "security": [{"session_auth": []}],
                "responses": {
                    "200": {"description": "Form rendered"},
                    "401": {"description": "Unauthorized"},
                    "403": {"description": "Forbidden"},
                },
            },
            "post": {
                "tags": ["Plans"],
                "summary": "Create new plan",
                "description": "Creates a new subscription plan. Admin access required.",
                "security": [{"session_auth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string", "minLength": 1},
                                    "description": {"type": "string"},
                                    "price": {"type": "number", "format": "float", "minimum": 0},
                                    "duration_days": {"type": "integer", "minimum": 1},
                                },
                                "required": ["name", "price", "duration_days"],
                            }
                        }
                    },
                },
                "responses": {
                    "302": {"description": "Plan created"},
                    "200": {"description": "Validation error"},
                    "401": {"description": "Unauthorized"},
                    "403": {"description": "Forbidden"},
                },
            },
        },
    )

    # GET/POST /plans/edit/<plan_id>
    add_path(
        spec,
        "/plans/edit/{plan_id}",
        {
            "get": {
                "tags": ["Plans"],
                "summary": "Display plan edit form",
                "description": "Renders plan edit form. Admin access required.",
                "security": [{"session_auth": []}],
                "parameters": [
                    {
                        "name": "plan_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "responses": {
                    "200": {"description": "Form rendered"},
                    "404": {"description": "Plan not found"},
                    "401": {"description": "Unauthorized"},
                    "403": {"description": "Forbidden"},
                },
            },
            "post": {
                "tags": ["Plans"],
                "summary": "Update plan",
                "description": "Updates plan information. Admin access required.",
                "security": [{"session_auth": []}],
                "parameters": [
                    {
                        "name": "plan_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "description": {"type": "string"},
                                    "price": {"type": "number", "format": "float"},
                                    "duration_days": {"type": "integer"},
                                },
                            }
                        }
                    },
                },
                "responses": {
                    "302": {"description": "Plan updated"},
                    "404": {"description": "Plan not found"},
                    "401": {"description": "Unauthorized"},
                    "403": {"description": "Forbidden"},
                },
            },
        },
    )

    # POST /plans/delete/<plan_id>
    add_path(
        spec,
        "/plans/delete/{plan_id}",
        {
            "post": {
                "tags": ["Plans"],
                "summary": "Delete plan",
                "description": "Deletes a subscription plan. Admin access required.",
                "security": [{"session_auth": []}],
                "parameters": [
                    {
                        "name": "plan_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "responses": {
                    "302": {"description": "Plan deleted"},
                    "404": {"description": "Plan not found"},
                    "401": {"description": "Unauthorized"},
                    "403": {"description": "Forbidden"},
                },
            }
        },
    )

    # GET /plans/view/<plan_id>
    add_path(
        spec,
        "/plans/view/{plan_id}",
        {
            "get": {
                "tags": ["Plans"],
                "summary": "View plan details",
                "description": "Displays detailed information about a plan. Admin access required.",
                "security": [{"session_auth": []}],
                "parameters": [
                    {
                        "name": "plan_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Plan details retrieved",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/PlanSchema"}
                            }
                        },
                    },
                    "404": {"description": "Plan not found"},
                    "401": {"description": "Unauthorized"},
                    "403": {"description": "Forbidden"},
                },
            }
        },
    )


def document_domain_routes(spec: APISpec) -> None:
    """Document domain management routes."""

    for route in [
        "/domains/",
        "/domains/create",
        "/domains/edit/{domain_id}",
        "/domains/delete/{domain_id}",
        "/domains/view/{domain_id}",
    ]:
        if route == "/domains/":
            add_path(
                spec,
                route,
                {
                    "get": {
                        "tags": ["Domains"],
                        "summary": "List all domains",
                        "description": "Retrieves list of all domains. Admin access required.",
                        "security": [{"session_auth": []}],
                        "responses": {
                            "200": {
                                "description": "Domains retrieved",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "$ref": "#/components/schemas/DomainListResponse"
                                        }
                                    }
                                },
                            },
                            "401": {"description": "Unauthorized"},
                            "403": {"description": "Forbidden"},
                        },
                    }
                },
            )
        elif route == "/domains/create":
            add_path(
                spec,
                route,
                {
                    "get": {
                        "tags": ["Domains"],
                        "summary": "Display domain creation form",
                        "security": [{"session_auth": []}],
                        "responses": {"200": {"description": "Form rendered"}},
                    },
                    "post": {
                        "tags": ["Domains"],
                        "summary": "Create new domain",
                        "description": "Creates a new domain. Super admin only.",
                        "security": [{"session_auth": []}],
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/x-www-form-urlencoded": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "name": {"type": "string"},
                                            "cloudflare_api": {"type": "string"},
                                            "cloudflare_email": {
                                                "type": "string",
                                                "format": "email",
                                            },
                                            "cloudflare_password": {"type": "string"},
                                            "cloudflare_status": {"type": "boolean"},
                                        },
                                        "required": ["name"],
                                    }
                                }
                            },
                        },
                        "responses": {
                            "302": {"description": "Domain created"},
                            "401": {"description": "Unauthorized"},
                            "403": {"description": "Forbidden"},
                        },
                    },
                },
            )
        elif "/edit/" in route:
            add_path(
                spec,
                route,
                {
                    "get": {
                        "tags": ["Domains"],
                        "summary": "Display domain edit form",
                        "security": [{"session_auth": []}],
                        "parameters": [
                            {
                                "name": "domain_id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string"},
                            }
                        ],
                        "responses": {
                            "200": {"description": "Form rendered"},
                            "404": {"description": "Not found"},
                        },
                    },
                    "post": {
                        "tags": ["Domains"],
                        "summary": "Update domain",
                        "security": [{"session_auth": []}],
                        "parameters": [
                            {
                                "name": "domain_id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string"},
                            }
                        ],
                        "responses": {
                            "302": {"description": "Updated"},
                            "404": {"description": "Not found"},
                        },
                    },
                },
            )
        elif "/delete/" in route:
            add_path(
                spec,
                route,
                {
                    "post": {
                        "tags": ["Domains"],
                        "summary": "Delete domain",
                        "security": [{"session_auth": []}],
                        "parameters": [
                            {
                                "name": "domain_id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string"},
                            }
                        ],
                        "responses": {
                            "302": {"description": "Deleted"},
                            "404": {"description": "Not found"},
                        },
                    }
                },
            )
        elif "/view/" in route:
            add_path(
                spec,
                route,
                {
                    "get": {
                        "tags": ["Domains"],
                        "summary": "View domain details",
                        "security": [{"session_auth": []}],
                        "parameters": [
                            {
                                "name": "domain_id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string"},
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "Details retrieved",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/DomainSchema"}
                                    }
                                },
                            },
                            "404": {"description": "Not found"},
                        },
                    }
                },
            )


def document_template_routes(spec: APISpec) -> None:
    """Document template management routes."""

    for route in [
        "/templates/",
        "/templates/create",
        "/templates/edit/{template_id}",
        "/templates/delete/{template_id}",
        "/templates/view/{template_id}",
    ]:
        if route == "/templates/":
            add_path(
                spec,
                route,
                {
                    "get": {
                        "tags": ["Templates"],
                        "summary": "List all templates",
                        "security": [{"session_auth": []}],
                        "responses": {
                            "200": {
                                "description": "Templates retrieved",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "$ref": "#/components/schemas/TemplateListResponse"
                                        }
                                    }
                                },
                            }
                        },
                    }
                },
            )
        elif route == "/templates/create":
            add_path(
                spec,
                route,
                {
                    "get": {
                        "tags": ["Templates"],
                        "summary": "Display template creation form",
                        "security": [{"session_auth": []}],
                        "responses": {"200": {"description": "Form rendered"}},
                    },
                    "post": {
                        "tags": ["Templates"],
                        "summary": "Create new template",
                        "security": [{"session_auth": []}],
                        "responses": {"302": {"description": "Template created"}},
                    },
                },
            )
        elif "/edit/" in route:
            add_path(
                spec,
                route,
                {
                    "get": {
                        "tags": ["Templates"],
                        "summary": "Display template edit form",
                        "security": [{"session_auth": []}],
                        "parameters": [
                            {
                                "name": "template_id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string"},
                            }
                        ],
                        "responses": {"200": {"description": "Form rendered"}},
                    },
                    "post": {
                        "tags": ["Templates"],
                        "summary": "Update template",
                        "security": [{"session_auth": []}],
                        "parameters": [
                            {
                                "name": "template_id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string"},
                            }
                        ],
                        "responses": {"302": {"description": "Updated"}},
                    },
                },
            )
        elif "/delete/" in route:
            add_path(
                spec,
                route,
                {
                    "post": {
                        "tags": ["Templates"],
                        "summary": "Delete template",
                        "security": [{"session_auth": []}],
                        "parameters": [
                            {
                                "name": "template_id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string"},
                            }
                        ],
                        "responses": {"302": {"description": "Deleted"}},
                    }
                },
            )
        elif "/view/" in route:
            add_path(
                spec,
                route,
                {
                    "get": {
                        "tags": ["Templates"],
                        "summary": "View template details",
                        "security": [{"session_auth": []}],
                        "parameters": [
                            {
                                "name": "template_id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string"},
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "Details retrieved",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/TemplateSchema"}
                                    }
                                },
                            }
                        },
                    }
                },
            )


def document_info_routes(spec: APISpec) -> None:
    """Document banking information management routes."""

    add_path(
        spec,
        "/infos/",
        {
            "get": {
                "tags": ["Infos"],
                "summary": "List all banking information",
                "security": [{"session_auth": []}],
                "responses": {
                    "200": {
                        "description": "Infos retrieved",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/InfoListResponse"}
                            }
                        },
                    }
                },
            }
        },
    )
    add_path(
        spec,
        "/infos/client/{client_id}",
        {
            "get": {
                "tags": ["Infos"],
                "summary": "Get banking info by client",
                "security": [{"session_auth": []}],
                "parameters": [
                    {
                        "name": "client_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "responses": {"200": {"description": "Infos retrieved"}},
            }
        },
    )
    add_path(
        spec,
        "/infos/create/{client_id}",
        {
            "get": {
                "tags": ["Infos"],
                "summary": "Display info creation form",
                "security": [{"session_auth": []}],
                "parameters": [
                    {
                        "name": "client_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "responses": {"200": {"description": "Form rendered"}},
            },
            "post": {
                "tags": ["Infos"],
                "summary": "Create new banking info",
                "security": [{"session_auth": []}],
                "parameters": [
                    {
                        "name": "client_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "agencia": {"type": "string"},
                                    "conta": {"type": "string"},
                                    "saldo": {"type": "number", "format": "float"},
                                    "status": {"type": "string"},
                                },
                                "required": ["agencia", "conta"],
                            }
                        }
                    },
                },
                "responses": {"302": {"description": "Info created"}},
            },
        },
    )
    add_path(
        spec,
        "/infos/edit/{info_id}",
        {
            "get": {
                "tags": ["Infos"],
                "summary": "Display info edit form",
                "security": [{"session_auth": []}],
                "parameters": [
                    {
                        "name": "info_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "responses": {"200": {"description": "Form rendered"}},
            },
            "post": {
                "tags": ["Infos"],
                "summary": "Update banking info",
                "security": [{"session_auth": []}],
                "parameters": [
                    {
                        "name": "info_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "responses": {"302": {"description": "Updated"}},
            },
        },
    )
    add_path(
        spec,
        "/infos/view/{info_id}",
        {
            "get": {
                "tags": ["Infos"],
                "summary": "View banking info details",
                "security": [{"session_auth": []}],
                "parameters": [
                    {
                        "name": "info_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Details retrieved",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/InfoSchema"}
                            }
                        },
                    }
                },
            }
        },
    )
    add_path(
        spec,
        "/infos/delete/{info_id}",
        {
            "post": {
                "tags": ["Infos"],
                "summary": "Delete banking info",
                "security": [{"session_auth": []}],
                "parameters": [
                    {
                        "name": "info_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "responses": {"302": {"description": "Deleted"}},
            }
        },
    )
