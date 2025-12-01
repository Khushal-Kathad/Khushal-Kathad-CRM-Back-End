================================================================================
                        CRM BACKEND API DOCUMENTATION
================================================================================
Version: 1.0
Base URL: http://localhost:8080
Framework: FastAPI (Python)
Database: Microsoft SQL Server (Azure SQL Database)
Authentication: JWT Bearer Token

================================================================================
                              TABLE OF CONTENTS
================================================================================
1. Authentication & Security
2. User Management
3. Lead Management
4. Contact Management
5. Follow-Up Management
6. Site Management
7. Visit Management
8. Role Management
9. Infrastructure Management
10. Permission Management
11. Admin Operations
12. Reporting APIs
13. Common Response Formats
14. Error Handling

================================================================================
                         1. AUTHENTICATION & SECURITY
================================================================================

## Overview
The API uses JWT (JSON Web Token) authentication with OAuth2 password bearer scheme.
Tokens expire after 24 hours.

## Login Endpoint

### POST /auth/token
Login with username and password to receive access token.

**Request Body:**
```
Content-Type: application/x-www-form-urlencoded

username: string (required)
password: string (required)
```

**Response:** 200 OK
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error Responses:**
- 401 Unauthorized: Invalid credentials

### GET /auth/verify-token/{token}
Verify if a JWT token is valid.

**Path Parameters:**
- token: string (required) - JWT token to verify

**Response:** 200 OK
```json
{
  "message": "Token is valid"
}
```

**Error Responses:**
- 403 Forbidden: Token is invalid or expired

## Using Authentication
Include the JWT token in all subsequent requests:
```
Authorization: Bearer <access_token>
```

================================================================================
                           2. USER MANAGEMENT
================================================================================

### GET /user/
Get all users in the system.

**Headers:** Authorization: Bearer <token>

**Response:** 200 OK
```json
[
  {
    "id": 1,
    "FirstName": "John",
    "LastName": "Doe",
    "Email": "john.doe@example.com",
    "username": "johndoe",
    "is_active": true,
    "ManagerId": null,
    "ContactNo": 9876543210,
    "CreatedDate": "2024-01-15T10:30:00",
    "UpdatedDate": "2024-01-15T10:30:00",
    "CreatedBy": 1
  }
]
```

### GET /user/get-single-user/{user_id}
Get a single user by ID with role information.

**Path Parameters:**
- user_id: integer > 0 (required)

**Response:** 200 OK
```json
{
  "id": 1,
  "FirstName": "John",
  "LastName": "Doe",
  "Email": "john.doe@example.com",
  "username": "johndoe",
  "is_active": true,
  "ManagerId": null,
  "ContactNo": 9876543210,
  "CreatedDate": "2024-01-15T10:30:00",
  "UpdatedDate": "2024-01-15T10:30:00",
  "CreatedBy": 1,
  "RoleIds": [1, 2, 3]
}
```

### POST /user/create-users
Create a new user with role assignments.

**Request Body:**
```json
{
  "username": "newuser",
  "email": "newuser@example.com",
  "first_name": "New",
  "last_name": "User",
  "password": "SecurePassword123!",
  "is_active": true,
  "ManagerId": 1,
  "ContactNo": 9876543210,
  "RoleAssignments": [1, 2]
}
```

**Response:** 201 Created
```json
{
  "id": 10,
  "message": "User created successfully",
  "roles": [1, 2],
  "user_role_ids": [101, 102]
}
```

### PUT /user/update-user/{user_id}
Update user details and role assignments.

**Path Parameters:**
- user_id: integer (required)

**Request Body:**
```json
{
  "FirstName": "Updated",
  "LastName": "Name",
  "Email": "updated@example.com",
  "username": "updateduser",
  "is_active": true,
  "ManagerId": 2,
  "ContactNo": 9876543211,
  "RoleAssignments": [2, 3, 4]
}
```

**Response:** 200 OK
```json
{
  "id": 10,
  "message": "User updated successfully",
  "roles": [2, 3, 4],
  "user_role_ids": [103, 104, 105]
}
```

### GET /user/currentuser
Get details of the currently authenticated user.

**Response:** 200 OK
```json
{
  "id": 1,
  "FirstName": "Current",
  "LastName": "User",
  "Email": "current@example.com",
  "username": "currentuser",
  "is_active": true,
  "ManagerId": null,
  "ContactNo": 9876543210,
  "CreatedDate": "2024-01-15T10:30:00",
  "UpdatedDate": "2024-01-15T10:30:00",
  "CreatedBy": null
}
```

### PUT /user/updatepass
Update password for the current user.

**Request Body:**
```json
{
  "password": "currentPassword123",
  "new_password": "newSecurePassword456!"
}
```

**Response:** 204 No Content

**Error Responses:**
- 401 Unauthorized: Current password incorrect

================================================================================
                           3. LEAD MANAGEMENT
================================================================================

### GET /leads/lead_search
Search leads with filters and related data.

**Query Parameters:**
- query: string (optional) - Search by lead name
- contactId: string (optional) - Filter by contact ID
- brokerId: string (optional) - Filter by broker ID

**Response:** 200 OK
```json
[
  {
    "type": "lead",
    "data": {
      "LeadId": 1,
      "LeadName": "Residential Plot Lead",
      "ContactId": 5,
      "SiteId": 2,
      "InfraId": 3,
      "InfraUnitId": 10,
      "ProspectTypeId": 1,
      "CreatedById": 1,
      "LeadCreatedDate": "2024-01-15T10:30:00",
      "LeadClosedDate": null,
      "UpdatedDate": "2024-01-20T15:45:00",
      "QuotedAmount": 5000000,
      "RequestedAmount": 4800000,
      "ClosedAmount": null,
      "LeadStatus": "Open",
      "BrokerId": 3,
      "LeadType": "Hot",
      "LeadSource": "Website",
      "SuggestedUnitId": 10,
      "Bedrooms": 3,
      "SizeSqFt": 1500,
      "ViewType": "Garden",
      "FloorPreference": "Ground",
      "BuyingIntent": "High",
      "LeadPriority": "High",
      "LeadNotes": "Customer looking for immediate possession",
      "Direction": "North",
      "Locality": "Downtown",
      "LostReasons": null,
      "contacts": { /* full contact object */ },
      "created_by": { /* full user object */ },
      "broker": { /* full broker object */ },
      "prospecttypes": { /* full prospect type object */ },
      "site": { /* full site object */ },
      "SuggestedUnit": {
        "InfraUnitId": 10,
        "UnitNumber": 101
      }
    }
  }
]
```

### GET /leads/
Get all leads created by the current user.

**Response:** 200 OK
```json
[
  {
    "LeadId": 1,
    "LeadName": "Residential Plot Lead",
    "ContactId": 5,
    "SiteId": 2,
    "InfraId": 3,
    /* ... all lead fields ... */
  }
]
```

### GET /leads/getsinglelead/{lead_id}
Get a single lead by ID.

**Path Parameters:**
- lead_id: integer > 0 (required)

**Response:** 200 OK
```json
{
  "LeadId": 1,
  "LeadName": "Residential Plot Lead",
  /* ... all lead fields ... */
}
```

### POST /leads/CreateLead
Create a new lead.

**Request Body:**
```json
{
  "LeadName": "New Commercial Lead",
  "ContactId": 5,
  "SiteId": 2,
  "InfraId": 3,
  "InfraUnitId": 10,
  "ProspectTypeId": 1,
  "QuotedAmount": 5000000,
  "RequestedAmount": 4800000,
  "ClosedAmount": null,
  "LeadStatus": "Open",
  "BrokerId": 3,
  "LeadType": "Hot",
  "LeadSource": "Website",
  "SuggestedUnitId": 10,
  "Bedrooms": 3,
  "SizeSqFt": 1500,
  "ViewType": "Garden",
  "FloorPreference": "Ground",
  "BuyingIntent": "High",
  "LeadPriority": "High",
  "LeadNotes": "Urgent requirement",
  "Direction": "North",
  "Locality": "Downtown",
  "LostReasons": null
}
```

**Response:** 201 Created
```json
{
  "LeadId": 25
}
```

### PUT /leads/LeadUpdate/{leadid}
Full update of a lead.

**Path Parameters:**
- leadid: integer (required)

**Request Body:** Same as Create Lead

**Response:** 204 No Content

### PATCH /leads/LeadUpdate/{leadid}
Partial update of a lead. Automatically sets LeadClosedDate when status is "Win" or "Lost".

**Path Parameters:**
- leadid: integer (required)

**Request Body:** Any subset of lead fields
```json
{
  "LeadStatus": "Win",
  "ClosedAmount": 4900000
}
```

**Response:** 204 No Content

### DELETE /leads/LeadDelete/{leadid}
Delete a lead.

**Path Parameters:**
- leadid: integer > 0 (required)

**Response:** 204 No Content

### GET /leads/count/{statustext}
Get count of leads by status.

**Path Parameters:**
- statustext: string (required) - Lead status (e.g., "Open", "Win", "Lost")

**Response:** 200 OK
```json
{
  "lead_count": 15
}
```

### GET /leads/sitewisecount/
Get lead count by site and status.

**Response:** 200 OK
```json
{
  "Downtown Plaza": {
    "Open": 10,
    "Win": 5,
    "Lost": 2
  },
  "Green Valley": {
    "Open": 8,
    "Win": 3,
    "Lost": 1
  }
}
```

### GET /leads/leads_full_detail
Get paginated lead details with all related data.

**Query Parameters:**
- sIndex: integer (default=1) - Start index (1-based)
- limit: integer (default=20) - Number of records per page

**Response:** 200 OK
```json
{
  "data": [
    {
      "LeadId": 1,
      "LeadName": "Residential Plot Lead",
      /* ... all lead fields with related objects ... */
    }
  ],
  "total_records": 150,
  "sIndex": 1,
  "limit": 20,
  "nextIndex": 21
}
```

================================================================================
                         4. CONTACT MANAGEMENT
================================================================================

### GET /contact/
Get all contacts with lead count, paginated.

**Query Parameters:**
- sIndex: integer (default=1) - Start index (1-based)
- limit: integer (default=20) - Number of records per page

**Response:** 200 OK
```json
{
  "data": [
    {
      "ContactId": 1,
      "ContactFName": "John",
      "ContactLName": "Smith",
      "ContactEmail": "john.smith@email.com",
      "ContactNo": 9876543210,
      "ContactCity": "Mumbai",
      "ContactState": "Maharashtra",
      "ContactAddress": "123 Main Street",
      "ContactPostalCode": "400001",
      "ContactCountryCode": "+91",
      "ContactType": "Individual",
      "CreatedDate": "2024-01-15T10:30:00",
      "UpdatedDate": "2024-01-15T10:30:00",
      "CreatedById": 1,
      "leadcount": 5
    }
  ],
  "count": 20,
  "total_records": 100,
  "sIndex": 1,
  "limit": 20,
  "nextIndex": 21
}
```

### GET /contact/getsinglecontact/{contact_id}
Get a single contact by ID.

**Path Parameters:**
- contact_id: integer > 0 (required)

**Response:** 200 OK
```json
{
  "ContactId": 1,
  "ContactFName": "John",
  "ContactLName": "Smith",
  /* ... all contact fields ... */
}
```

### POST /contact/createcontact
Create a new contact. Contact number must be unique.

**Request Body:**
```json
{
  "ContactFName": "Jane",
  "ContactLName": "Doe",
  "ContactEmail": "jane.doe@email.com",
  "ContactNo": 9876543211,
  "ContactCity": "Delhi",
  "ContactState": "Delhi",
  "ContactAddress": "456 Park Avenue",
  "ContactPostalCode": "110001",
  "ContactCountryCode": "+91",
  "ContactType": "Individual"
}
```

**Response:** 201 Created
```json
{
  "ContactId": 50
}
```

**Error Responses:**
- 400 Bad Request: Contact with this ContactNo already exists

### PUT /contact/updatecontact/{contact_id}
Update contact details.

**Path Parameters:**
- contact_id: integer (required)

**Request Body:** Same as Create Contact

**Response:** 204 No Content

**Error Responses:**
- 400 Bad Request: Another contact with this ContactNo already exists

### DELETE /contact/deletecontact/{contact_id}
Delete a contact.

**Path Parameters:**
- contact_id: integer > 0 (required)

**Response:** 204 No Content

**Error Responses:**
- 400 Bad Request: Cannot delete contact because it is referenced by other records

### GET /contact/contact_search
Search contacts by various criteria.

**Query Parameters:**
- query: string (optional) - Search in ContactNo, FirstName, LastName, ContactId
- contact_type: string (optional) - Filter by contact type

**Response:** 200 OK
```json
[
  {
    "type": "contact",
    "data": {
      "ContactId": 1,
      "ContactNo": 9876543210,
      "ContactFName": "John",
      "ContactLName": "Smith",
      "ContactType": "Individual"
    }
  }
]
```

### GET /contact/count/{statustext}
Get lead count for a specific contact by status.

**Path Parameters:**
- statustext: string (required) - Lead status

**Query Parameters:**
- ContactId: integer (required) - Contact ID

**Response:** 200 OK
```json
{
  "lead_count": 5
}
```

### GET /contact/sitewisecount/
Get lead count by site and status for a specific contact.

**Query Parameters:**
- ContactId: integer (required) - Contact ID

**Response:** 200 OK
```json
{
  "Downtown Plaza": {
    "Open": 3,
    "Win": 1,
    "Lost": 0
  }
}
```

================================================================================
                        5. FOLLOW-UP MANAGEMENT
================================================================================

### GET /Follow_Ups/
Get all follow-ups.

**Response:** 200 OK
```json
[
  {
    "FollowUpsId": 1,
    "LeadId": 5,
    "VisitId": 10,
    "UserId": 2,
    "FollowUpType": "Phone",
    "Status": "Pending",
    "Notes": "Discuss pricing options",
    "FollowUpDate": "2024-01-20T14:00:00",
    "NextFollowUpDate": "2024-01-25T14:00:00",
    "CreatedDate": "2024-01-15T10:30:00",
    "UpdatedDate": "2024-01-15T10:30:00",
    "CreatedById": 1
  }
]
```

### GET /Follow_Ups/getsinglefollowups/{follow_id}
Get a single follow-up by ID.

**Path Parameters:**
- follow_id: integer > 0 (required)

**Response:** 200 OK - Returns follow-up object

### POST /Follow_Ups/createfollowups
Create a new follow-up. Validates that Lead, Visit, and User exist.

**Request Body:**
```json
{
  "LeadId": 5,
  "VisitId": 10,
  "UserId": 2,
  "FollowUpType": "Phone",
  "Status": "Pending",
  "Notes": "Discuss pricing options",
  "FollowUpDate": "2024-01-20T14:00:00",
  "NextFollowUpDate": "2024-01-25T14:00:00",
  "CreatedDate": "2024-01-15T10:30:00",
  "UpdatedDate": "2024-01-15T10:30:00",
  "CreatedById": 1
}
```

**Response:** 201 Created
```json
{
  "message": "Follow-up created successfully",
  "data": { /* follow-up object */ }
}
```

**Error Responses:**
- 400 Bad Request: LeadId/VisitId/UserId does not exist

### PUT /Follow_Ups/updatefollowups/{follow_id}
Update follow-up details.

**Path Parameters:**
- follow_id: integer (required)

**Request Body:** Same as Create Follow-up

**Response:** 204 No Content

### DELETE /Follow_Ups/deletefollowups/{follow_id}
Delete a follow-up.

**Path Parameters:**
- follow_id: integer > 0 (required)

**Response:** 204 No Content

### GET /Follow_Ups/follow-Ups-by-leadId/{Lead_id}
Get all follow-ups for a specific lead.

**Path Parameters:**
- Lead_id: integer > 0 (required)

**Response:** 200 OK
```json
[
  {
    "FollowUpsId": 1,
    "LeadId": 5,
    /* ... all follow-up fields ... */
  }
]
```

================================================================================
                          6. SITE MANAGEMENT
================================================================================

### GET /site/
Get all sites.

**Response:** 200 OK
```json
[
  {
    "SiteId": 1,
    "SiteName": "Green Valley Residential",
    "SiteTypeId": 2,
    "SiteCity": "Mumbai",
    "SiteAddress": "Plot 123, Sector 5",
    "SiteStatus": "Active",
    "SiteSizeSqFt": 50000,
    "OperationalDate": "2023-01-01",
    "IsOperational": true,
    "DeveloperId": 3,
    "SiteDescription": "Premium residential complex",
    "NearbyLandmarks": "Near Metro Station",
    "CreatedDate": "2023-01-01T10:00:00",
    "UpdateDate": "2024-01-15T15:30:00",
    "CreatedById": 1,
    "isDelete": false
  }
]
```

### GET /site/getsinglesite/{site_id}
Get a single site by ID.

**Path Parameters:**
- site_id: integer > 0 (required)

**Response:** 200 OK - Returns site object

### POST /site/createsite
Create a new site.

**Request Body:**
```json
{
  "SiteName": "Sunrise Commercial Complex",
  "SiteTypeId": 3,
  "SiteCity": "Delhi",
  "SiteAddress": "Block A, Connaught Place",
  "SiteStatus": "Under Construction",
  "SiteSizeSqFt": 75000,
  "OperationalDate": "2025-06-01",
  "IsOperational": false,
  "DeveloperId": 5,
  "SiteDescription": "Modern commercial space",
  "NearbyLandmarks": "Central Business District"
}
```

**Response:** 201 Created
```json
{
  "SiteId": 10
}
```

### PUT /site/updatesite/{site_id}
Update site details.

**Path Parameters:**
- site_id: integer (required)

**Request Body:** Same as Create Site

**Response:** 204 No Content

### DELETE /site/deletesite/{site_id}
Delete a site. Checks for dependencies in Visit, SiteInfra, Lead, and AmenitySite tables.

**Path Parameters:**
- site_id: integer > 0 (required)

**Response:** 204 No Content

**Error Responses:**
- 400 Bad Request: Cannot delete - SiteId is used in [table names]

### GET /site/site-full-details
Get all sites with related data (site type, developer, created by).

**Response:** 200 OK
```json
[
  {
    "SiteId": 1,
    "SiteName": "Green Valley Residential",
    /* ... all site fields ... */
    "sitetype": { /* site type object */ },
    "developer": { /* developer object */ },
    "created_by": { /* user object */ }
  }
]
```

================================================================================
                          7. VISIT MANAGEMENT
================================================================================

### GET /visit/
Get all visits.

**Response:** 200 OK
```json
[
  {
    "VisitId": 1,
    "InfraId": 3,
    "SiteId": 2,
    "VisitDate": "2024-01-15T14:30:00",
    "VisitStatus": "Completed",
    "SalesPersonId": 5,
    "Purpose": "Site Tour",
    "UpdatedDate": "2024-01-15T16:00:00",
    "VisitOutlook": "Positive",
    "CreatedDate": "2024-01-15T10:00:00",
    "CreatedById": 1,
    "isDelete": false
  }
]
```

### GET /visit/get_single_visit/{visit_id}
Get a single visit by ID.

**Path Parameters:**
- visit_id: integer > 0 (required)

**Response:** 200 OK - Returns visit object

### PUT /visit/updatevisit/{visit_id}
Update visit details (limited fields).

**Path Parameters:**
- visit_id: integer (required)

**Request Body:**
```json
{
  "InfraId": 3,
  "SiteId": 2,
  "VisitDate": "2024-01-20T14:30:00",
  "VisitStatus": "Scheduled",
  "SalesPersonId": 5,
  "Purpose": "Follow-up Visit",
  "VisitOutlook": "Neutral"
}
```

**Response:** 204 No Content

### DELETE /visit/deletevisit/{visit_id}
Delete a visit.

**Path Parameters:**
- visit_id: integer > 0 (required)

**Response:** 204 No Content

### GET /visit/Visit_full_details/
Get paginated visit details with related site, infrastructure, and created by information.

**Query Parameters:**
- sIndex: integer (default=1) - Start index (1-based)
- limit: integer (default=20) - Number of records per page

**Response:** 200 OK
```json
{
  "data": [
    {
      "VisitId": 1,
      /* ... all visit fields ... */
      "site": {
        "SiteId": 2,
        "SiteName": "Green Valley",
        "SiteAddress": "Plot 123, Sector 5"
      },
      "infra": {
        "InfraId": 3,
        "InfraName": "Tower A",
        "InfraCategory": "Residential"
      },
      "created_by": {
        "id": 1,
        "FirstName": "John",
        "LastName": "Doe"
      }
    }
  ],
  "total_records": 100,
  "total_pages": 5,
  "current_page": 1,
  "limit": 20,
  "nextIndex": 2
}
```

### GET /visit/Visit_full_details/{visit_id}
Get single visit with full related data.

**Path Parameters:**
- visit_id: integer > 0 (required)

**Response:** 200 OK - Returns visit with related objects

### GET /visit/site-wise-count
Get visit count grouped by site.

**Response:** 200 OK
```json
[
  {
    "SiteId": 1,
    "SiteName": "Green Valley",
    "VisitCount": 25
  },
  {
    "SiteId": 2,
    "SiteName": "Sunrise Complex",
    "VisitCount": 18
  }
]
```

### GET /visit/visit_leads/{lead_id}
Get all visits associated with a lead (through Visitors table).

**Path Parameters:**
- lead_id: integer > 0 (required)

**Response:** 200 OK
```json
[
  {
    "VisitId": 1,
    /* ... visit fields with site and infra data ... */
  }
]
```

================================================================================
                          8. ROLE MANAGEMENT
================================================================================

### GET /Roles/
Get all roles.

**Response:** 200 OK
```json
[
  {
    "RoleId": 1,
    "Name": "Sales Manager",
    "Description": "Manages sales team",
    "IsSystemRole": false,
    "Active": true,
    "HierarchyLevel": 2,
    "CreatedBy": 1,
    "CreatedDate": "2024-01-01T10:00:00",
    "UpdatedDate": "2024-01-15T15:30:00"
  }
]
```

### GET /Roles/get-single-Roles/{roles_id}
Get a single role with associated site IDs.

**Path Parameters:**
- roles_id: integer > 0 (required)

**Response:** 200 OK
```json
{
  "RoleId": 1,
  "Name": "Sales Manager",
  "Description": "Manages sales team",
  "CreatedBy": 1,
  "CreatedDate": "2024-01-01T10:00:00",
  "UpdatedDate": "2024-01-15T15:30:00",
  "Sites": [1, 2, 3]
}
```

### POST /Roles/Create-Roles
Create a new role with site permissions.

**Request Body:**
```json
{
  "Name": "Regional Manager",
  "Description": "Manages regional operations",
  "IsSystemRole": false,
  "Active": true,
  "HierarchyLevel": 3,
  "site": [1, 2, 5]
}
```

**Response:** 201 Created
```json
{
  "role_id": 10,
  "permission_id": 20,
  "filter_id": 30,
  "filter_value_ids": [101, 102, 103],
  "assignment_ids": [201, 202, 203],
  "message": "Role created successfully with dynamic permission and site mappings"
}
```

**Error Responses:**
- 400 Bad Request: Role with name already exists

### PUT /Roles/update-Role/{role_id}
Update role details.

**Path Parameters:**
- role_id: integer (required)

**Request Body:**
```json
{
  "Name": "Updated Role Name",
  "Description": "Updated description",
  "IsSystemRole": false,
  "Active": true,
  "HierarchyLevel": 3
}
```

**Response:** 204 No Content

### DELETE /Roles/delete-Role/{role_id}
Delete a role. Checks if role is assigned to any users.

**Path Parameters:**
- role_id: integer > 0 (required)

**Response:** 204 No Content

**Error Responses:**
- 400 Bad Request: Cannot delete Role ID X because it is assigned to Y user(s)

================================================================================
                      9. INFRASTRUCTURE MANAGEMENT
================================================================================

## Infrastructure APIs

### GET /infra/
Get all infrastructure records.

**Headers:** Authorization: Bearer <token>

**Response:** 200 OK
```json
[
  {
    "InfraId": 1,
    "InfraName": "Tower A",
    "InfraCategory": "Residential",
    "TotalUnits": "100",
    "AvailableUnits": 25,
    "SoldUnits": 70,
    "BookedUnits": 5,
    "InfraFloorCount": 15,
    "SiteId": 2,
    "CreatedDate": "2023-06-01T10:00:00",
    "UpdatedDate": "2024-01-15T15:30:00",
    "CreatedById": 1,
    "isDelete": false
  }
]
```

### GET /infra/getsingleinfra/{infra_id}
Get a single infrastructure by ID.

**Headers:** Authorization: Bearer <token>

**Path Parameters:**
- infra_id: integer > 0 (required)

**Response:** 200 OK - Returns infrastructure object

**Error Responses:**
- 404 Not Found: infra not found

### POST /infra/createinfra
Create new infrastructure.

**Headers:** Authorization: Bearer <token>

**Request Body:**
```json
{
  "InfraName": "Tower B",
  "InfraCategory": "Commercial",
  "TotalUnits": "50",
  "AvailableUnits": 50,
  "SoldUnits": 0,
  "BookedUnits": 0,
  "InfraFloorCount": 10,
  "SiteId": 2
}
```

**Response:** 201 Created
```json
{
  "InfraId": 5
}
```

### PUT /infra/updateinfra/{infra_id}
Update infrastructure details.

**Headers:** Authorization: Bearer <token>

**Path Parameters:**
- infra_id: integer (required)

**Request Body:** Same as Create Infrastructure

**Response:** 204 No Content

**Error Responses:**
- 404 Not Found: infra not found

### DELETE /infra/deleteinfra/{infra_id}
Delete infrastructure. Checks for dependencies in InfraUnit, SiteInfra, and Visit tables.

**Headers:** Authorization: Bearer <token>

**Path Parameters:**
- infra_id: integer > 0 (required)

**Response:** 204 No Content

**Error Responses:**
- 404 Not Found: Infra not found
- 400 Bad Request: 
```json
{
  "detail": {
    "InfraId": 1,
    "message": "Cannot delete: InfraId is used in the following table(s): InfraUnit, SiteInfra, Visit"
  }
}
```

## Infrastructure Unit APIs

### GET /infra_unit/
Get all infrastructure units.

**Response:** 200 OK
```json
[
  {
    "InfraUnitId": 1,
    "InfraId": 1,
    "UnitNumber": 101,
    "FloorNumber": 1,
    "UnitSize": 1200.5,
    "AvailabilityStatus": "Available",
    "Direction": "North",
    "UnitType": "2BHK",
    "View": "Garden",
    "PurchaseReason": "Investment",
    "InfraType": "Residential",
    "Active": true,
    "CreatedDate": "2023-06-15T10:00:00",
    "UpdateDate": "2024-01-15T15:30:00",
    "CreatedById": 1
  }
]
```

### GET /infra_unit/getsingleinfraunit/{infra_unit_id}
Get a single infrastructure unit by ID.

**Path Parameters:**
- infra_unit_id: integer > 0 (required)

**Response:** 200 OK - Returns infrastructure unit object

### POST /infra_unit/create-InfraUnit
Create multiple infrastructure units and automatically create corresponding SiteInfra records.

**Request Body:**
```json
[
  {
    "InfraId": 1,
    "UnitNumber": 201,
    "FloorNumber": 2,
    "UnitSize": 1500.0,
    "AvailabilityStatus": "Available",
    "Direction": "East",
    "UnitType": "3BHK",
    "View": "Sea",
    "PurchaseReason": "Self Use",
    "InfraType": "Residential",
    "Active": true
  },
  {
    "InfraId": 1,
    "UnitNumber": 202,
    "FloorNumber": 2,
    "UnitSize": 1500.0,
    "AvailabilityStatus": "Booked",
    "Direction": "West",
    "UnitType": "3BHK",
    "View": "City",
    "PurchaseReason": "Investment",
    "InfraType": "Residential",
    "Active": true
  }
]
```

**Response:** 201 Created
```json
{
  "message": "2 InfraUnits and 2 SiteInfra records created successfully",
  "infraunit_ids": [10, 11],
  "siteinfra_ids": [20, 21]
}
```

### PUT /infra_unit/updateinfraunit/{infra_unit_id}
Update infrastructure unit details.

**Path Parameters:**
- infra_unit_id: integer (required)

**Request Body:**
```json
{
  "InfraId": 1,
  "UnitNumber": 201,
  "FloorNumber": 2,
  "UnitSize": 1550.0,
  "AvailabilityStatus": "Sold",
  "Direction": "East",
  "UnitType": "3BHK",
  "View": "Sea",
  "PurchaseReason": "Self Use"
}
```

**Response:** 204 No Content

### DELETE /infra_unit/deleteinfraunit/{infra_unit_id}
Delete infrastructure unit.

**Path Parameters:**
- infra_unit_id: integer > 0 (required)

**Response:** 204 No Content

### GET /infra_unit/search
Search infrastructure units with multiple filters.

**Query Parameters:**
- query: string (optional) - General search (floor, unit number, size, status, etc.)
- floor_number: integer (optional) - Filter by floor
- direction: string (optional) - Filter by direction
- unit_type: string (optional) - Filter by unit type
- view: string (optional) - Filter by view
- site_id: integer (optional) - Filter by site

**Response:** 200 OK
```json
[
  {
    "FloorNumber": 2,
    "UnitNumber": 201,
    "UnitSize": 1500.0,
    "AvailabilityStatus": "Available",
    "Direction": "East",
    "UnitType": "3BHK",
    "View": "Sea",
    "InfraUnitId": 10,
    "InfraId": 1
  }
]
```

### GET /infra_unit/option_search
Similar to /search but returns data in a different format.

**Response:** 200 OK
```json
[
  {
    "type": "infra_unit",
    "data": {
      "FloorNumber": 2,
      "UnitNumber": 201,
      "UnitSize": 1500.0,
      "AvailabilityStatus": "Available",
      "Direction": "East",
      "UnitType": "3BHK",
      "View": "Sea",
      "InfraUnitId": 10
    }
  }
]
```

================================================================================
                        10. PERMISSION MANAGEMENT
================================================================================

### GET /Permissions/
Get all permissions.

**Response:** 200 OK
```json
[
  {
    "PermissionId": 1,
    "Name": "Read Sites",
    "Code": "site.read",
    "PermissionType": "DATA",
    "ResourceType": "site",
    "OperationType": "Read",
    "Active": true,
    "CreatedAt": "2024-01-01T10:00:00",
    "UpdatedAt": "2024-01-15T15:30:00"
  }
]
```

### GET /Permissions/get-single-Permission/{permission_id}
Get a single permission by ID.

**Path Parameters:**
- permission_id: integer > 0 (required)

**Response:** 200 OK - Returns permission object

### POST /Permissions/Create-Permission
Create a new permission.

**Request Body:**
```json
{
  "Name": "Write Leads",
  "Code": "lead.write",
  "PermissionType": "DATA",
  "ResourceType": "lead",
  "OperationType": "Write",
  "Active": true
}
```

**Response:** 201 Created
```json
{
  "Permission-id": 5
}
```

### DELETE /Permissions/delete-Permission/{Permission_id}
Delete a permission.

**Path Parameters:**
- Permission_id: integer > 0 (required)

**Response:** 204 No Content

================================================================================
                         11. ADMIN OPERATIONS
================================================================================

### GET /admin/todo
Get all todos (admin only).

**Headers:** Authorization: Bearer <token> (User must have admin role)

**Response:** 200 OK - Returns list of todos

**Error Responses:**
- 401 Unauthorized: Admin access required

### DELETE /admin/todo/{todo_id}
Delete a todo (admin only).

**Path Parameters:**
- todo_id: integer > 0 (required)

**Headers:** Authorization: Bearer <token> (User must have admin role)

**Response:** 204 No Content

**Error Responses:**
- 401 Unauthorized: Admin access required

================================================================================
                          12. REPORTING APIs
================================================================================

Various reporting endpoints are available for:
- Weekly Site Visit Reports
- Conversion Reports
- Monthly Broker Reports
- Custom analytics

These endpoints typically include date range filters and return aggregated data.

================================================================================
                      13. COMMON RESPONSE FORMATS
================================================================================

## Success Response Format
Most list endpoints return data in this format:
```json
{
  "data": [...],
  "message": "Success message",
  "statusCode": 200,
  "totalRecords": 100
}
```

## Paginated Response Format
```json
{
  "data": [...],
  "total_records": 100,
  "sIndex": 1,
  "limit": 20,
  "nextIndex": 21
}
```

## Error Response Format
```json
{
  "detail": "Error description"
}
```

For validation errors:
```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "validation error message",
      "type": "error_type"
    }
  ]
}
```

================================================================================
                          14. ERROR HANDLING
================================================================================

## HTTP Status Codes

- **200 OK**: Successful GET, PUT
- **201 Created**: Successful POST
- **204 No Content**: Successful DELETE, PUT (no response body)
- **400 Bad Request**: Invalid request data, constraint violations
- **401 Unauthorized**: Missing or invalid authentication
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **422 Unprocessable Entity**: Validation errors
- **500 Internal Server Error**: Server-side errors

## Common Error Scenarios

1. **Authentication Failed**
   - Status: 401
   - Response: `{"detail": "Authentication Failed"}`

2. **Resource Not Found**
   - Status: 404
   - Response: `{"detail": "[Resource] not found"}`

3. **Duplicate Entry**
   - Status: 400
   - Response: `{"detail": "[Field] already exists"}`

4. **Foreign Key Constraint**
   - Status: 400
   - Response: `{"detail": "Cannot delete: [Resource] is referenced by other records"}`

5. **Validation Error**
   - Status: 422
   - Response includes field-specific validation messages

================================================================================
                              NOTES
================================================================================

1. **Authentication**: All endpoints except /auth/token require JWT authentication
2. **Soft Deletes**: Most entities use soft delete (isDelete flag)
3. **Timestamps**: All dates are in ISO 8601 format
4. **IDs**: All IDs are UNIQUEIDENTIFIER (UUID) in the database
5. **Pagination**: 1-based indexing for sIndex parameter
6. **Phone Numbers**: Must be 10-digit numbers (Indian format)
7. **CORS**: Currently configured to allow all origins (development setting)

================================================================================
                          END OF DOCUMENTATION
================================================================================