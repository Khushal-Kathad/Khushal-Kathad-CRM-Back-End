from fastapi import APIRouter, Depends, HTTPException,status
from pytz import timezone
from fastapi import Path
from pydantic import BaseModel,Field
from models import Role, Permission, PermissionFilter,PermissionFilterValue, PermissionAssignment, UserRole
from typing import Annotated
from sqlalchemy.orm import Session,joinedload, load_only
from sqlalchemy import  select, func
from database import SessionLocal
from .auth import get_current_user
from datetime import datetime
from schemas.schemas import RolesRequest


router = APIRouter(
    prefix="/Roles",
    tags = ['Roles']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_time():
    ind_time = datetime.now(timezone("Asia/Kolkata"))
    return ind_time

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get('/')
async def read_Roles(user:user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return db.query(Role).all()


#
# @router.get('/get-single-Roles/{roles_id}', status_code=status.HTTP_200_OK)
# async def Read_Roles(user:user_dependency, db: db_dependency, roles_id: int = Path(gt=0)):
#     if user is None:
#         raise HTTPException(status_code=401, detail="Authentication Failed")
#     Role_model = db.query(Role).filter(Role.RoleId == roles_id).first()
#     if Role_model is not None:
#         # return Role_model
#         raise HTTPException(status_code=404, detail=' Role not found')



@router.get('/get-single-Roles/{roles_id}', status_code=status.HTTP_200_OK)
async def Read_Roles(user: user_dependency, db: db_dependency, roles_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    # 1. Fetch Role
    role_model = db.query(Role).filter(Role.RoleId == roles_id).first()
    if not role_model:
        raise HTTPException(status_code=404, detail="Role not found")


    # 2. Get all PermissionAssignments for this role
    assignments = db.query(PermissionAssignment).filter(
        PermissionAssignment.RoleId == roles_id
    ).all()

    if not assignments:
        site_ids = []
    else:
        site_ids = []
        # 3. For each assigned permission, get its filters
        for assignment in assignments:
            filters = db.query(PermissionFilter).filter(
                PermissionFilter.PermissionId == assignment.PermissionId
            ).all()

            # 4. For each filter, get site IDs from PermissionFilterValue
            for f in filters:
                filter_values = db.query(PermissionFilterValue).filter(
                    PermissionFilterValue.FilterId == f.FilterId
                ).all()
                site_ids.extend([fv.Sequence for fv in filter_values])

        # Remove duplicates if same site is repeated
        site_ids = list(set(site_ids))

    # 5. Prepare response
    return {
        "RoleId": role_model.RoleId,
        "Name": role_model.Name,
        "Description": role_model.Description,
        "CreatedBy": role_model.CreatedBy,
        "CreatedDate": role_model.CreatedDate,
        "UpdatedDate": role_model.UpdatedDate,
        "Sites": site_ids
    }







# @router.post("/Create-Roles", status_code=status.HTTP_201_CREATED)
# async def create_roles(user: user_dependency, db: db_dependency, role_request: RolesRequest):
#     if user is None:
#         raise HTTPException(status_code=401, detail="Authentication Failed")
#
#     try:
#         # 1. Check if Role already exists
#         existing_role = db.query(Role).filter(Role.Name == role_request.Name).first()
#         if existing_role:
#             raise HTTPException(
#                 status_code=400,
#                 detail=f"Role with name '{role_request.Name}' already exists"
#             )
#
#         # 2. Create Role (exclude site since it's not a DB column)
#         role_model = Role(
#             **role_request.dict(exclude={"site"}),
#             CreatedBy=user.get("id"),
#             CreatedDate=get_time(),
#             UpdatedDate=get_time()
#         )
#         db.add(role_model)
#         db.flush()  # Get RoleId
#
#         # 3. Get PermissionFilter from DB
#         filter_model = db.query(PermissionFilter).first()
#         if not filter_model:
#             raise HTTPException(status_code=404, detail="No PermissionFilter found in DB")
#
#         # 4. Insert PermissionFilterValue(s) for each site_id
#         filter_value_ids = []
#         assignment_ids = []
#
#         for site_id in role_request.site:
#             filter_value_model = PermissionFilterValue(
#                 FilterId=filter_model.FilterId,
#                 Value="site_id"  ,  # store site_id as string
#                 ValueType="STRING",     # mark as string
#                 Sequence=site_id        # site_id used in sequence
#             )
#             db.add(filter_value_model)
#             db.flush()  # Get ValueId
#             filter_value_ids.append(filter_value_model.ValueId)
#
#             # 5. Create PermissionAssignment for Role
#             assignment_model = PermissionAssignment(
#                 PermissionId=filter_model.PermissionId,
#                 UserId=None,
#                 RoleId=role_model.RoleId,
#                 AssignmentType="ROLE",
#                 IsGranted=True,
#                 ExpiresAt=None,
#                 Reason=None,
#                 GrantedBy=user.get("id"),
#                 GrantedAt=get_time(),
#                 UpdatedAt=get_time()
#             )
#             db.add(assignment_model)
#             db.flush()
#             assignment_ids.append(assignment_model.AssignmentId)
#
#         # 6. Commit once
#         db.commit()
#
#         return {
#             "role_id": role_model.RoleId,
#             "filter_value_ids": filter_value_ids,
#             "assignment_ids": assignment_ids,
#             "sites": role_request.site,
#             "message": "Role created with default filter values and assignments"
#         }
#
#     except HTTPException:
#         raise
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail=str(e))



@router.post("/Create-Roles", status_code=status.HTTP_201_CREATED)
async def create_roles(user: user_dependency, db: db_dependency, role_request: RolesRequest):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    try:
        # 1. Check if Role already exists
        existing_role = db.query(Role).filter(Role.Name == role_request.Name).first()
        if existing_role:
            raise HTTPException(
                status_code=400,
                detail=f"Role with name '{role_request.Name}' already exists"
            )

        # 2. Create Role
        role_model = Role(
            **role_request.dict(exclude={"site"}),
            CreatedBy=user.get("id"),
            CreatedDate=get_time(),
            UpdatedDate=get_time()
        )
        db.add(role_model)
        db.flush()  # Get RoleId

        # 3. Create Permission (default fixed values)
        permission_model = Permission(
            Name="read sites",
            Code="site.read",
            PermissionType="DATA",
            ResourceType="site",
            OperationType="Read",
            Active=True,
            CreatedAt=get_time(),
            UpdatedAt=get_time()
            # CreatedBy=user.get('id')
        )
        db.add(permission_model)
        db.flush()  # Get PermissionId

        # 4. Create PermissionFilter for this Permission
        filter_model = PermissionFilter(
            PermissionId=permission_model.PermissionId,
            MasterAttribute = "site",
            Operator = "In",
            DataHierarchy = "All",
            CreatedAt=get_time()
        )
        db.add(filter_model)
        db.flush()  # Get FilterId

        # 5. Insert PermissionFilterValues for site IDs
        filter_value_ids = []
        assignment_ids = []

        for site_id in role_request.site:
            filter_value_model = PermissionFilterValue(
                FilterId=filter_model.FilterId,
                Value=str(site_id),
                ValueType="STRING",
                Sequence=site_id
            )
            db.add(filter_value_model)
            db.flush()
            filter_value_ids.append(filter_value_model.ValueId)

            # 6. Create PermissionAssignment for Role
            assignment_model = PermissionAssignment(
                PermissionId=permission_model.PermissionId,
                UserId=None,
                RoleId=role_model.RoleId,
                AssignmentType="ROLE",
                IsGranted=True,
                ExpiresAt=None,
                Reason=None,
                GrantedBy=user.get("id"),
                GrantedAt=get_time(),
                UpdatedAt=get_time()
            )
            db.add(assignment_model)
            db.flush()
            assignment_ids.append(assignment_model.AssignmentId)

        # 7. Commit once
        db.commit()

        return {
            "role_id": role_model.RoleId,
            "permission_id": permission_model.PermissionId,
            "filter_id": filter_model.FilterId,
            "filter_value_ids": filter_value_ids,
            "assignment_ids": assignment_ids,
            "message": "Role created successfully with dynamic permission and site mappings"
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))














@router.put("/update_Roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT )
async def update_Roles (user: user_dependency,db: db_dependency,role_id: int, roles_request:RolesRequest):
    if user is None:
        raise HTTPException (status_code=401, detail='Authentication Failed')
    existing_role = db.query(Role).filter(Role.RoleId == role_id).filter(Role.CreatedBy == user.get('id') ).first()
    if existing_role is None:
        raise HTTPException (status_code=404, detail=" roles not found")
    existing_role.Name = roles_request.Name
    existing_role.Description = roles_request.Description
    existing_role.IsSystem = roles_request.IsSystemRole
    existing_role.Active = roles_request.Active
    existing_role.HierarchyLevel = roles_request.HierarchyLevel
    existing_role.UpdatedDate = get_time()
    db.add(existing_role)
    db.commit()



@router.delete("/delete-roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_roles (user: user_dependency, db: db_dependency, role_id : int =Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    roles_model = db.query(Role).filter(Role.RoleId== role_id).first()
    if  roles_model is None:
        raise HTTPException(status_code=404, detail=" Roles not found")

    # Fetch users assigned to this role
    assigned_users = db.query(UserRole.UserId).filter(UserRole.RoleId == role_id).all()
    if assigned_users:
        # Extract User IDs from result
        user_ids = [u.UserId for u in assigned_users]
        raise HTTPException(
            status_code=400,
            detail={
                "message": f"Cannot delete Role ID {role_id} because it is assigned to {len(user_ids)} user(s).",
                "assigned_user_ids": user_ids
            }
        )

    try:
        # Delete related records first (foreign key constraints)
        # 1. Delete PermissionAssignments for this role
        assignments = db.query(PermissionAssignment).filter(PermissionAssignment.RoleId == role_id).all()

        permission_ids = set()
        for assignment in assignments:
            permission_ids.add(assignment.PermissionId)
            db.delete(assignment)

        # 2. For each permission, delete its filters and filter values
        for permission_id in permission_ids:
            # Get filters for this permission
            filters = db.query(PermissionFilter).filter(PermissionFilter.PermissionId == permission_id).all()

            for filter_obj in filters:
                # Delete filter values
                db.query(PermissionFilterValue).filter(PermissionFilterValue.FilterId == filter_obj.FilterId).delete()
                # Delete filter
                db.delete(filter_obj)

            # Delete permission
            permission = db.query(Permission).filter(Permission.PermissionId == permission_id).first()
            if permission:
                db.delete(permission)

        # 3. Finally delete the role
        db.delete(roles_model)
        db.commit()
        return {"message": "Role deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting role: {str(e)}")