from fastapi import APIRouter, Depends, HTTPException,status
from fastapi import Path
from pydantic import BaseModel, Field, conint
from models import Todos, Users, UserRole
from typing import Annotated, List, Optional
from sqlalchemy.orm import Session
from database import SessionLocal
from .auth import get_current_user, bcrypt_context, CreateUserRequest
from passlib.context import CryptContext
from datetime import datetime, timedelta
from pytz import timezone

router = APIRouter(
    prefix="/user",
    tags = ['users']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


def get_time():
    ind_time = datetime.now(timezone("Asia/Kolkata"))
    return ind_time


class UpdatedPassRequest(BaseModel):
    password: str
    new_password: str


class UserResponse(BaseModel):
    id: int
    FirstName: str
    LastName: str
    Email: str
    username: str
    is_active: bool
    ManagerId: int | None = None
    ContactNo: Optional[conint(ge=1000000000, le=9999999999)]
    CreatedDate: Optional[datetime] = None
    UpdatedDate: Optional[datetime] = None
    CreatedBy: Optional[int] = None
    # RoleAssignments: List[int]



class UpdateUserResponse(BaseModel):
    FirstName: str
    LastName: str
    Email: str
    username: str
    is_active: bool
    ManagerId: int | None = None
    # ContactNo: Optional[conint]
    ContactNo: Optional[conint(ge=1000000000, le=9999999999)]
    # RoleAssignments: List[int]
    RoleAssignments: Optional[List[int]]






# @router.get('/')
# async def read_users( user:user_dependency,db: db_dependency):
#     if user is None:
#         raise HTTPException (status_code=401, detail='Authentication Failed')
#     return db.query(Users).all()


@router.get('/', response_model=List[UserResponse])
async def read_users(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return db.query(Users).all()






# @router.get("/get-single-user{user_id}", status_code=status.HTTP_200_OK)
# async def get_user_by_id(user: user_dependency, db: db_dependency, user_id: int = Path(gt=0)):
#     if user is None:
#         raise HTTPException(status_code=401, detail='Authentication Failed')
#     user_model = db.query(Users).filter(Users.id == user_id).first()
#     if user_model is not None:
#         return user_model
#     raise HTTPException(status_code=404, detail='User not found')


# @router.get("/get-single-user/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
# async def get_user_by_id(user: user_dependency, db: db_dependency, user_id: int = Path(gt=0)):
#     if user is None:
#         raise HTTPException(status_code=401, detail='Authentication Failed')
#     user_model = db.query(Users).filter(Users.id == user_id).first()
#     if user_model is not None:
#         return user_model
#     raise HTTPException(status_code=404, detail='User not found')


@router.get("/get-single-user/{user_id}", status_code=status.HTTP_200_OK)
async def get_user_by_id(user: user_dependency, db: db_dependency, user_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    # Step 1: Fetch User Details
    user_model = db.query(Users).filter(Users.id == user_id).first()
    if not user_model:
        raise HTTPException(status_code=404, detail='User not found')

    # Step 2: Fetch RoleIds from UserRoles Table
    role_ids = db.query(UserRole.RoleId).filter(UserRole.UserId == user_id).all()
    role_ids = [r.RoleId for r in role_ids]  # Convert to list

    # Step 3: Return Custom JSON Response (No need to add RoleIds in Pydantic)
    return {
        "id": user_model.id,
        "FirstName": user_model.FirstName,
        "LastName": user_model.LastName,
        "Email": user_model.Email,
        "username": user_model.username,
        "is_active": user_model.is_active,
        "ManagerId": user_model.ManagerId,
        "ContactNo": user_model.ContactNo,
        "CreatedDate": user_model.CreatedDate,
        "UpdatedDate": user_model.UpdatedDate,
        "CreatedBy": user_model.CreatedBy,
        "RoleIds": role_ids
    }








# @router.post ("/create-users",status_code=status.HTTP_201_CREATED)
# async def create_user(user: user_dependency,db: db_dependency,create_user_request: CreateUserRequest):
#     create_user_model= Users(
#         Email= create_user_request.email,
#         username = create_user_request.username,
#         FirstName = create_user_request.first_name,
#         LastName = create_user_request.last_name,
#         hashedpassword = bcrypt_context.hash(create_user_request.password),
#         # is_active = True
#         is_active = create_user_request.is_active,
#         ManagerId = create_user_request.ManagerId,
#         ContactNo = create_user_request.ContactNo,
#         CreatedDate = get_time(),
#         UpdatedDate = get_time(),
#         CreatedBy = user.get('id')
#     )
#     db.add(create_user_model)
#     # db.commit()
#     db.flush()  # Ensures `id` is generated before commit
#     user_id = create_user_model.id
#     db.commit()
#     return {"id": user_id, "message": "User created successfully"}





# @router.post ("/create-users",status_code=status.HTTP_201_CREATED)
# async def create_user(user: user_dependency,db: db_dependency,create_user_request: CreateUserRequest):
#     create_user_model= Users(
#         Email= create_user_request.email,
#         username = create_user_request.username,
#         FirstName = create_user_request.first_name,
#         LastName = create_user_request.last_name,
#         hashedpassword = bcrypt_context.hash(create_user_request.password),
#         # is_active = True
#         is_active = create_user_request.is_active,
#         ManagerId = create_user_request.ManagerId,
#         ContactNo = create_user_request.ContactNo,
#         RoleAssignments = create_user_request.RoleAssignments,
#         CreatedDate = get_time(),
#         UpdatedDate = get_time(),
#         CreatedBy = user.get('id')
#     )
#     db.add(create_user_model)
#     # db.commit()
#     db.flush()  # Ensures `id` is generated before commit
#     user_id = create_user_model.id
#     db.commit()
#     return {"id": user_id, "message": "User created successfully"}


# ----------------------------------------------------------------------------------------------------


@router.post("/create-users", status_code=status.HTTP_201_CREATED)
async def create_user(user: user_dependency,db: db_dependency,create_user_request: CreateUserRequest):
    # Step 1: Check if username already exists
    existing_user = db.query(Users).filter(Users.username == create_user_request.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    # Step 2: Create User
    create_user_model = Users(
        Email=create_user_request.email,
        username=create_user_request.username,
        FirstName=create_user_request.first_name,
        LastName=create_user_request.last_name,
        hashedpassword=bcrypt_context.hash(create_user_request.password),
        is_active=create_user_request.is_active,
        ManagerId=create_user_request.ManagerId,
        ContactNo=create_user_request.ContactNo,
        CreatedDate=get_time(),
        UpdatedDate=get_time(),
        CreatedBy=user.get('id')
    )
    db.add(create_user_model)
    db.flush()  # Generate UserId before inserting roles

    # Step 3: Assign Roles
    user_roles = []
    for role_id in create_user_request.RoleAssignments:
        user_roles.append(
            UserRole(
                UserId=create_user_model.id,
                RoleId=role_id,
                IsActive=True,
                ExpiryDate=datetime(9999, 1, 1),
                Notes=None,
                AssignedBy=user.get('id'),
                CreatedDate=get_time(),
                UpdatedDate=get_time()
            )
        )
    db.add_all(user_roles)

    # Step 4: Commit transaction
    db.commit()
    for ur in user_roles:
        db.refresh(ur)

        # Collect UserRoleIds
    user_role_ids = [ur.UserRoleId for ur in user_roles]

    return {
        "id": create_user_model.id,
        "message": "User created successfully",
        "roles": create_user_request.RoleAssignments,
        "user_role_ids": user_role_ids
    }
    # db.refresh(create_user_model)
    #
    # return {
    #     "id": create_user_model.id,
    #     "message": "User created successfully",
    #     "roles": create_user_request.RoleAssignments
    # }












# @router.put("/Update-Users/{user_id}", status_code=status.HTTP_204_NO_CONTENT )
# async def update_users (user:user_dependency, db: db_dependency, user_id: int, user_request : UpdateUserResponse):
#     if user is None:
#         raise HTTPException(status_code=401, detail='auth failed')
#     existing_users = db.query(Users).filter(Users.id == user_id).first()
#     if existing_users is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     existing_users.username = user_request.username
#     existing_users.Email = user_request.Email
#     existing_users.FirstName = user_request.FirstName
#     existing_users.LastName = user_request.LastName
#     existing_users.is_active = user_request.is_active
#     existing_users.ManagerId = user_request.ManagerId
#     existing_users.ContactNo = user_request.ContactNo
#     existing_users.RoleAssignments = user_request.RoleAssignments
#     existing_users.UpdatedDate = get_time()
#     db.add(existing_users)
#     db.commit()





# ----------------------------------------------------------------------------------------
# @router.put("/update-user/{user_id}", status_code=status.HTTP_200_OK)
# async def update_user(user: user_dependency,db: db_dependency,user_id: int,update_user_request: UpdateUserResponse):
#     # Step 1: Check if user exists
#     existing_user = db.query(Users).filter(Users.id == user_id).first()
#     if not existing_user:
#         raise HTTPException(status_code=404, detail="User not found")
#
#     # Step 2: Update user fields (excluding password)
#     if update_user_request.Email is not None:
#         existing_user.Email = update_user_request.Email
#     if update_user_request.username is not None:
#         existing_user.username = update_user_request.username
#     if update_user_request.FirstName is not None:
#         existing_user.FirstName = update_user_request.FirstName
#     if update_user_request.LastName is not None:
#         existing_user.LastName = update_user_request.LastName
#     if update_user_request.is_active is not None:
#         existing_user.is_active = update_user_request.is_active
#     if update_user_request.ManagerId is not None:
#         existing_user.ManagerId = update_user_request.ManagerId
#     if update_user_request.ContactNo is not None:
#         existing_user.ContactNo = update_user_request.ContactNo
#
#     existing_user.UpdatedDate = get_time()
#
#     # Step 3: Update roles if provided
#     user_role_ids = []
#     if update_user_request.RoleAssignments is not None:
#         # Remove old roles
#         db.query(UserRole).filter(UserRole.UserId == user_id).delete()
#
#         # Add new roles
#         new_roles = []
#         for role_id in update_user_request.RoleAssignments:
#             new_roles.append(
#                 UserRole(
#                     UserId=user_id,
#                     RoleId=role_id,
#                     IsActive=True,
#                     ExpiryDate=datetime(9999, 1, 1),
#                     Notes=None,
#                     AssignedBy=user.get("id"),
#                     CreatedDate=get_time(),
#                     UpdatedDate=get_time()
#                 )
#             )
#         db.add_all(new_roles)
#         db.flush()
#
#         # Collect new UserRoleIds
#         user_role_ids = [nr.UserRoleId for nr in new_roles]
#
#     # Step 4: Commit changes
#     db.commit()
#     db.refresh(existing_user)
#
#     return {
#         "id": existing_user.id,
#         "message": "User updated successfully",
#         "roles": update_user_request.RoleAssignments,
#         "user_role_ids": user_role_ids
#     }


# ---------------------------------------------------------------------

@router.put("/update-user/{user_id}", status_code=status.HTTP_200_OK)
async def update_user(user: user_dependency,db: db_dependency,user_id: int,update_user_request: UpdateUserResponse):
    try:
        # Step 1: Check if user exists
        existing_user = db.query(Users).filter(Users.id == user_id).first()
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")

        # Step 2: Update user fields (excluding password)
        if update_user_request.Email is not None:
            existing_user.Email = update_user_request.Email
        if update_user_request.username is not None:
            existing_user.username = update_user_request.username
        if update_user_request.FirstName is not None:
            existing_user.FirstName = update_user_request.FirstName
        if update_user_request.LastName is not None:
            existing_user.LastName = update_user_request.LastName
        if update_user_request.is_active is not None:
            existing_user.is_active = update_user_request.is_active
        if update_user_request.ManagerId is not None:
            existing_user.ManagerId = update_user_request.ManagerId
        if update_user_request.ContactNo is not None:
            existing_user.ContactNo = update_user_request.ContactNo

        existing_user.UpdatedDate = get_time()

        # Step 3: Handle role updates intelligently
        user_role_ids = []
        if update_user_request.RoleAssignments is not None:
            # Get current roles from DB
            existing_roles = db.query(UserRole).filter(UserRole.UserId == user_id).all()
            existing_role_ids = {role.RoleId for role in existing_roles}
            new_role_ids = set(update_user_request.RoleAssignments)

            # Find roles to add (present in new but not in existing)
            roles_to_add = new_role_ids - existing_role_ids

            # Find roles to delete (present in existing but not in new)
            roles_to_delete = existing_role_ids - new_role_ids

            # Delete only roles that are not in the new list
            if roles_to_delete:
                for role_id in roles_to_delete:
                    db.query(UserRole).filter(
                        UserRole.UserId == user_id,
                        UserRole.RoleId == role_id
                    ).delete()

            # Add only new roles
            new_roles = []
            for role_id in roles_to_add:
                new_roles.append(
                    UserRole(
                        UserId=user_id,
                        RoleId=role_id,
                        IsActive=True,
                        ExpiryDate=datetime(9999, 1, 1),
                        Notes=None,
                        AssignedBy=user.get("id"),
                        CreatedDate=get_time(),
                        UpdatedDate=get_time()
                    )
                )
            if new_roles:
                db.add_all(new_roles)
                db.flush()
                user_role_ids.extend([nr.UserRoleId for nr in new_roles])

            # Keep existing roles
            existing_kept_roles = [role.UserRoleId for role in existing_roles if role.RoleId in new_role_ids]
            user_role_ids.extend(existing_kept_roles)

        # Step 4: Commit changes
        db.commit()
        db.refresh(existing_user)

        return {
            "id": existing_user.id,
            "message": "User updated successfully",
            "roles": update_user_request.RoleAssignments,
            "user_role_ids": user_role_ids
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating user: {str(e)}")





# @router.get("/currentuser", status_code=status.HTTP_200_OK)
# async def current_user (user:user_dependency, db: db_dependency):
#     if user is None:
#         raise HTTPException (status_code=401, detail='Authentication Failed')
#     user_model = db.query(Users).filter(Users.id==user.get('id')).first()
#     if user_model is not None:
#         return user_model
#     raise HTTPException(status_code=404, detail = 'User not found')






@router.get("/currentuser", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def current_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    if user_model is not None:
        return user_model
    raise HTTPException(status_code=404, detail='User not found')





@router.put("/updatepass", status_code=status.HTTP_204_NO_CONTENT )
async def update_pass (user:user_dependency, db: db_dependency, updated_pass_request:UpdatedPassRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='auth failed')
    user_model = db.query(Users).filter(Users.id==user.get('id')).first()
    if not bcrypt_context.verify(updated_pass_request.password,user_model.hashedpassword):
        raise HTTPException(status_code=401, detail = 'Error password change')
    user_model.hashedpassword =  bcrypt_context.hash(updated_pass_request.new_password)
    db.add(user_model)
    db.commit()