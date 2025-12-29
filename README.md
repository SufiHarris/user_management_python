# User Management System

A production-ready user management system built with FastAPI and PostgreSQL, featuring Role-Based Access Control (RBAC), multi-tenancy, and comprehensive permission management.

## Features

- ✅ Multi-tenant architecture
- ✅ User authentication with JWT
- ✅ Role-Based Access Control (RBAC)
- ✅ Flexible permission system
- ✅ Group management
- ✅ RESTful API with OpenAPI documentation
- ✅ ACID-compliant database operations
- ✅ Comprehensive error handling
- ✅ Database migrations with Alembic
- ✅ Password hashing with bcrypt
- ✅ UUID primary keys
- ✅ Audit trails (timestamps, created_by, etc.)

## Technology Stack

- **Framework**: FastAPI 0.109.0
- **Database**: PostgreSQL 15+
- **ORM**: SQLAlchemy 2.0.25
- **Migrations**: Alembic 1.13.1
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt (passlib)
- **Validation**: Pydantic 2.5.3

## Database Schema

The system includes 11 tables:

1. **tenant_master** - Multi-tenant support
2. **user_details** - User information
3. **role_master** - Role definitions
4. **permission_master** - Permission definitions
5. **group_master** - Group definitions
6. **user_role_mapping** - User-Role assignments
7. **permission_user_mapping** - Direct user permissions
8. **role_permission_mapping** - Role-Permission assignments
9. **group_user_mapping** - Group-User assignments
10. **group_role_mapping** - Group-Role assignments
11. **group_permission_mapping** - Group-Permission assignments

## Installation

### Prerequisites

- Python 3.10+
- PostgreSQL 15+
- macOS (instructions are Mac-specific)

### Setup Steps

1. **Install PostgreSQL**

```bash
brew install postgresql@15
brew services start postgresql@15
```

2. **Create Database**

```bash
psql postgres
CREATE DATABASE user_management_db;
CREATE USER app_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE user_management_db TO app_user;
\q
```

3. **Clone and Setup Project**

```bash
mkdir user_management && cd user_management
python3 -m venv venv
source venv/bin/activate
```

4. **Install Dependencies**

```bash
pip install -r requirements.txt
```

5. **Configure Environment**

```bash
cp .env.example .env
# Edit .env with your settings
```

6. **Initialize Database**

```bash
# Run migrations
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head

# Or create tables directly
python -c "from app.database import engine, Base; from app.models import *; Base.metadata.create_all(bind=engine)"
```

7. **Run Application**

```bash
uvicorn app.main:app --reload --port 8000
```

## API Documentation

Once the application is running, visit:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Tenants

- `POST /api/v1/tenants/` - Create tenant
- `GET /api/v1/tenants/{tenant_id}` - Get tenant
- `GET /api/v1/tenants/` - List tenants
- `PUT /api/v1/tenants/{tenant_id}` - Update tenant
- `DELETE /api/v1/tenants/{tenant_id}` - Delete tenant

### Users

- `POST /api/v1/users/register` - Register user
- `POST /api/v1/users/login` - Login user
- `GET /api/v1/users/{user_id}` - Get user
- `GET /api/v1/users/` - List users
- `PUT /api/v1/users/{user_id}` - Update user
- `DELETE /api/v1/users/{user_id}` - Delete user

### Roles

- `POST /api/v1/roles/` - Create role
- `GET /api/v1/roles/{role_id}` - Get role
- `GET /api/v1/roles/` - List roles
- `PUT /api/v1/roles/{role_id}` - Update role
- `DELETE /api/v1/roles/{role_id}` - Delete role
- `POST /api/v1/roles/assign-user` - Assign role to user
- `DELETE /api/v1/roles/remove-user/{user_id}/{role_id}` - Remove role from user
- `GET /api/v1/roles/user/{user_id}/roles` - Get user roles

### Permissions

- `POST /api/v1/permissions/` - Create permission
- `GET /api/v1/permissions/{permission_id}` - Get permission
- `GET /api/v1/permissions/` - List permissions
- `PUT /api/v1/permissions/{permission_id}` - Update permission
- `DELETE /api/v1/permissions/{permission_id}` - Delete permission
- `POST /api/v1/permissions/assign-user` - Assign permission to user
- `POST /api/v1/permissions/assign-role` - Assign permission to role
- `GET /api/v1/permissions/user/{user_id}/permissions` - Get user permissions

## Usage Examples

### 1. Create a Tenant

```bash
curl -X POST "http://localhost:8000/api/v1/tenants/" \
  -H "Content-Type: application/json" \
  -d '{"tenant_name": "Acme Corp"}'
```

### 2. Register a User

```bash
curl -X POST "http://localhost:8000/api/v1/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "YOUR_TENANT_ID",
    "firstname": "John",
    "lastname": "Doe",
    "email": "john@example.com",
    "password": "SecurePass123!"
  }'
```

### 3. Login

```bash
curl -X POST "http://localhost:8000/api/v1/users/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123!"
  }'
```

### 4. Create a Role

```bash
curl -X POST "http://localhost:8000/api/v1/roles/" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "YOUR_TENANT_ID",
    "role_name": "Admin",
    "description": "Administrator role"
  }'
```

### 5. Create a Permission

```bash
curl -X POST "http://localhost:8000/api/v1/permissions/" \
  -H "Content-Type: application/json" \
  -d '{
    "permission_name": "user.create",
    "resource": "user",
    "action": "create",
    "description": "Create users"
  }'
```

### 6. Assign Role to User

```bash
curl -X POST "http://localhost:8000/api/v1/roles/assign-user" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "USER_ID",
    "role_id": "ROLE_ID"
  }'
```

## Project Structure

```
user_management/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py              # Configuration settings
│   ├── database.py            # Database connection
│   ├── models/                # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── role.py
│   │   ├── permission.py
│   │   ├── tenant.py
│   │   └── group.py
│   ├── schemas/               # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── role.py
│   │   ├── permission.py
│   │   ├── tenant.py
│   │   ├── group.py
│   │   └── common.py
│   ├── api/                   # API endpoints
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── users.py
│   │       ├── roles.py
│   │       ├── permissions.py
│   │       └── tenants.py
│   ├── services/              # Business logic
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   ├── role_service.py
│   │   ├── permission_service.py
│   │   └── tenant_service.py
│   └── utils/                 # Utility functions
│       ├── __init__.py
│       ├── security.py
│       └── helpers.py
├── alembic/                   # Database migrations
│   ├── versions/
│   └── env.py
├── tests/                     # Test files
│   └── __init__.py
├── .env                       # Environment variables
├── .env.example              # Example environment file
├── requirements.txt          # Python dependencies
├── alembic.ini              # Alembic configuration
└── README.md                # This file
```
