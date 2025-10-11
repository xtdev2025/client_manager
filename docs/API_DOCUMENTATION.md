# 📚 API Documentation Guide

## Overview

The Client Manager application includes comprehensive API documentation using Swagger/OpenAPI 3.0.3.

## Accessing the Documentation

### Swagger UI
Interactive documentation: **http://localhost:5000/api/docs**

### OpenAPI Specification
Raw JSON spec: **http://localhost:5000/api/swagger.json**

## Statistics

- **63 endpoints** documented across **46 unique paths**
- **10 functional modules** with organized tags
- **Pydantic schemas** for validation
- **Session-based authentication**

## Endpoints by Category

### Main (2)
- `GET /` - Home page
- `GET /dashboard` - Dashboard

### Auth (7)
- `GET/POST /auth/login` - Login
- `GET /auth/logout` - Logout  
- `GET/POST /auth/register` - Register client
- `GET/POST /auth/register_admin` - Register admin

### Clients (10)
- `GET /clients/` - List all
- `GET/POST /clients/create` - Create
- `GET/POST /clients/edit/<id>` - Edit
- `POST /clients/delete/<id>` - Delete
- `GET /clients/view/<id>` - View
- Domain management (3 endpoints)

### Client Portal (5)
- `GET /client/my-domains` - My domains
- `GET /client/my-click-stats` - Statistics
- `GET /client/my-infos` - Banking info
- `GET/POST /client/my-change-password` - Change password

### Admins (8)
- `GET /admins/` - List all
- `GET/POST /admins/create` - Create
- `GET/POST /admins/edit/<id>` - Edit
- `POST /admins/delete/<id>` - Delete
- `GET/POST /admins/profile` - Profile

### Audit (2)
- `GET /admins/audit-logs` - View logs
- `POST /admins/clear-audit-logs` - Clear logs

### Plans, Domains, Templates, Infos
Each with 5-8 CRUD endpoints

## Authentication

1. Login: `POST /auth/login`
2. Session cookie automatically set
3. Use for authenticated requests
4. Logout: `GET /auth/logout`

## Permission Levels

- **Public**: No auth required
- **Client**: Client login required
- **Admin**: Admin/super_admin role
- **Super Admin**: super_admin role only

## Rate Limiting

- Login: 10/minute
- Admin registration: 5/minute
