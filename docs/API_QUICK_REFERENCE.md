# 🚀 API Quick Reference

## Access Points

| Resource | URL | Description |
|----------|-----|-------------|
| **Swagger UI** | `http://localhost:5000/api/docs` | Interactive API documentation |
| **OpenAPI Spec** | `http://localhost:5000/api/swagger.json` | Raw OpenAPI 3.0.3 JSON |

## Authentication

```bash
# Login
curl -X POST http://localhost:5000/auth/login \
  -d "username=admin&password=admin123" \
  -c cookies.txt

# Use session cookie for authenticated requests
curl -X GET http://localhost:5000/dashboard \
  -b cookies.txt

# Logout
curl -X GET http://localhost:5000/auth/logout \
  -b cookies.txt
```

## Quick Stats

- **63 endpoints** across **10 modules**
- **46 unique paths**
- **Session-based** authentication
- **OpenAPI 3.0.3** specification

## Modules

| Module | Endpoints | Access |
|--------|-----------|--------|
| **Main** | 2 | Public/Authenticated |
| **Auth** | 7 | Public/Super Admin |
| **Clients** | 10 | Admin |
| **Client Portal** | 5 | Client |
| **Admins** | 8 | Admin/Super Admin |
| **Plans** | 7 | Admin |
| **Domains** | 7 | Admin/Super Admin |
| **Templates** | 7 | Admin |
| **Infos** | 8 | Admin |
| **Audit** | 2 | Admin/Super Admin |

## Permission Levels

| Level | Description | Routes |
|-------|-------------|--------|
| **Public** | No auth required | `/`, `/auth/login`, `/auth/register` |
| **Client** | Client login | `/client/my-*` |
| **Admin** | Admin/Super Admin | Most `/clients`, `/plans`, etc. |
| **Super Admin** | Super Admin only | `/auth/register_admin`, `/domains/create` |

## Common Operations

### List Resources

```
GET /clients/          # List all clients
GET /admins/           # List all admins
GET /plans/            # List all plans
GET /domains/          # List all domains
GET /templates/        # List all templates
GET /infos/            # List all banking info
```

### View Details

```
GET /clients/view/<id>
GET /plans/view/<id>
GET /domains/view/<id>
GET /templates/view/<id>
GET /infos/view/<id>
```

### Create Resource

```
POST /clients/create
POST /plans/create
POST /domains/create
POST /templates/create
POST /infos/create/<client_id>
```

### Update Resource

```
POST /clients/edit/<id>
POST /plans/edit/<id>
POST /domains/edit/<id>
POST /templates/edit/<id>
POST /infos/edit/<id>
```

### Delete Resource

```
POST /clients/delete/<id>
POST /plans/delete/<id>
POST /domains/delete/<id>
POST /templates/delete/<id>
POST /infos/delete/<id>
```

## Client Portal

```
GET  /client/my-domains           # View my domains
GET  /client/my-click-stats        # View my statistics
GET  /client/my-infos              # View my banking info
GET  /client/my-change-password    # Password change form
POST /client/my-change-password    # Change password
```

## Response Formats

### Success

```json
{
  "message": "Operation successful",
  "data": { ... }
}
```

### Error

```json
{
  "error": "Error message",
  "code": 400
}
```

### Validation Error

```json
{
  "error": "Validation failed",
  "field": "username"
}
```

## Rate Limits

| Endpoint | Limit |
|----------|-------|
| `POST /auth/login` | 10/minute |
| `POST /auth/register_admin` | 5/minute |

## HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 302 | Redirect (after form submission) |
| 400 | Bad Request (validation error) |
| 401 | Unauthorized (not logged in) |
| 403 | Forbidden (insufficient permissions) |
| 404 | Not Found |
| 429 | Too Many Requests (rate limit) |
| 500 | Internal Server Error |

## Development

### Add New Endpoint Documentation

1. Edit `app/api/route_docs.py`
2. Add to appropriate `document_*_routes()` function
3. Restart Flask server
4. View at `/api/docs`

### Add New Schema

1. Edit `app/api/schemas.py`
2. Create Pydantic model
3. Reference in route documentation
4. Schema auto-registered in OpenAPI spec

## Support

- 📚 [Full API Documentation](API_DOCUMENTATION.md)
- 🏗️ [Architecture Guide](../ARCHITECTURE.md)
- 📖 [Main README](../README.md)
