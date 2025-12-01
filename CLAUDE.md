# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Application
```bash
# Development server with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8080

# Production server
uvicorn main:app --host 0.0.0.0 --port 8080

# Using Docker
docker-compose up
```

### Database Operations
```bash
# The application uses SQL Server on Azure. Connection details are in database.py
# Database URL format: mssql+pyodbc://username:password@server/database?driver=ODBC+Driver+17+for+SQL+Server
```

## Architecture Overview

### Core Components

1. **FastAPI Application** (main.py)
   - Entry point that initializes all routers
   - CORS configured for all origins (development setting)
   - 40+ router modules mounted under specific paths

2. **Database Layer** (database.py, models.py)
   - SQLAlchemy ORM with SQL Server backend
   - All models inherit from a Base class with common fields:
     - `Id` (UNIQUEIDENTIFIER primary key)
     - `CreatedDate`, `UpdatedDate` (automatic timestamps)
     - `CreatedById`, `UpdatedById` (audit fields)
     - `isDelete` (soft delete flag)

3. **Authentication System** (routers/auth.py)
   - JWT-based authentication with 24-hour expiration
   - Token payload includes: username, user_id, role, exp
   - Password hashing using bcrypt
   - OAuth2 password bearer scheme

4. **API Structure Pattern**
   - Routes organized by domain (lead, site, user, etc.)
   - Each router module typically includes:
     - CREATE (POST): Single entity creation
     - READ (GET): List with pagination and individual by ID
     - UPDATE (PUT): Modify existing entities
     - DELETE: Soft delete by setting isDelete=1
   - Response models use Pydantic schemas from /schemas directory

### Key Design Patterns

1. **Pagination**: Most list endpoints support pagination via `skip` and `limit` parameters
2. **Soft Deletes**: Entities are marked with `isDelete=1` rather than being removed
3. **Audit Trail**: All entities track creation and modification metadata
4. **Role-Based Access**: Users have roles that determine permissions
5. **Related Data Loading**: Many endpoints include related data (e.g., user includes roles)

### API Response Format
Standard response structure:
```json
{
  "data": [...],  // or single object
  "message": "Success message",
  "statusCode": 200,
  "totalRecords": 100  // for paginated responses
}
```

### Important Relationships
- **Infrastructure** (Infra) has many **InfraUnits**
- **Sites** belong to **Developers** and **InfraOwners**
- **Leads** have **Follow-ups** and **Lead History**
- **Users** have **Roles** through **UserRole** junction table
- **Permissions** are assigned to **Roles**

### Development Notes
- All IDs use UNIQUEIDENTIFIER (UUID) format
- Dates should be in ISO format for API requests
- File paths and imports assume Windows environment
- Redis is configured but usage pattern should be checked in individual routers
- Email templates are stored in /templates directory