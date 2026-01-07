# Authentication System

JWT-based authentication with multi-tenant support.

## Features

- ✅ JWT access tokens (15 min expiry)
- ✅ JWT refresh tokens (7 days expiry)
- ✅ Password hashing with bcrypt
- ✅ Multi-tenant user isolation
- ✅ Protected routes with dependency injection

## Endpoints

### POST /api/v1/auth/signup
Create a new tenant and admin user.

**Request:**
```json
{
  "tenant_name": "Acme Corp",
  "email": "admin@acme.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "user": {
    "id": 1,
    "tenant_id": 1,
    "email": "admin@acme.com",
    "role": "admin",
    "created_at": "2024-01-01T00:00:00"
  },
  "tenant": {
    "id": 1,
    "name": "Acme Corp",
    "email": "admin@acme.com",
    "created_at": "2024-01-01T00:00:00"
  }
}
```

### POST /api/v1/auth/login
Authenticate existing user.

**Request:**
```json
{
  "email": "admin@acme.com",
  "password": "securepassword123"
}
```

**Response:** Same as signup

### POST /api/v1/auth/refresh
Refresh access token using refresh token.

**Request:**
```json
{
  "refresh_token": "eyJ..."
}
```

**Response:**
```json
{
  "access_token": "eyJ..."
}
```

### GET /api/v1/auth/me
Get current user and tenant information (protected).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "user": {
    "id": 1,
    "tenant_id": 1,
    "email": "admin@acme.com",
    "role": "admin",
    "created_at": "2024-01-01T00:00:00"
  },
  "tenant": {
    "id": 1,
    "name": "Acme Corp",
    "email": "admin@acme.com",
    "created_at": "2024-01-01T00:00:00"
  }
}
```

## Using Authentication in Your Routes

### Protect a route with authentication:

```python
from fastapi import Depends
from app.core.dependencies import get_current_user, get_current_tenant
from app.models.user import User
from app.models.tenant import Tenant

@router.get("/protected")
async def protected_route(
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    return {
        "message": "This is protected",
        "user_id": current_user.id,
        "tenant_id": current_tenant.id,
    }
```

### JWT Token Payload

Access tokens contain:
```json
{
  "sub": 1,  // user_id
  "tenant_id": 1,
  "email": "admin@acme.com",
  "exp": 1234567890,
  "type": "access"
}
```

Refresh tokens contain:
```json
{
  "sub": 1,  // user_id
  "tenant_id": 1,
  "email": "admin@acme.com",
  "exp": 1234567890,
  "type": "refresh"
}
```

## Security Features

1. **Password Hashing**: All passwords are hashed using bcrypt
2. **Token Expiry**: Access tokens expire in 15 minutes, refresh tokens in 7 days
3. **Token Type Validation**: Access and refresh tokens are validated by type
4. **Tenant Isolation**: All tokens include tenant_id for multi-tenant isolation
5. **Bearer Token Authentication**: Uses HTTPBearer security scheme

## Configuration

Environment variables in `.env`:
```env
SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
```

