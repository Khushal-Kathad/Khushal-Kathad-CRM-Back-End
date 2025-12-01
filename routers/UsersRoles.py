from fastapi import APIRouter, Depends, HTTPException,status
from pytz import timezone
from fastapi import Path
from pydantic import BaseModel,Field
from models import UserRole
from typing import Annotated
from sqlalchemy.orm import Session,joinedload, load_only
from sqlalchemy import  select, func
from database import SessionLocal
from .auth import get_current_user
from datetime import datetime
from schemas.schemas import UsersRolesRequest


router = APIRouter(
    prefix="/UserRoles",
    tags = ['UserRoles']
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
async def Read_UserRoles(user:user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return db.query(UserRole).all()



@router.get('/get-single-user-roles/{userrole_id}', status_code=status.HTTP_200_OK)
async def Read_UserRoles(user:user_dependency, db: db_dependency, userrole_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    userRole_model = db.query(UserRole).filter(UserRole.UserRoleId == userrole_id).first()
    if userRole_model is not None:
        return userRole_model
    raise HTTPException(status_code=404, detail='user role not found')



# @router.post("/Create-user-roles", status_code=status.HTTP_201_CREATED)
# async def create_user_roles(user: user_dependency, db: db_dependency, userRole_request: UsersRolesRequest):
#     if user is None:
#         raise HTTPException(status_code=401, detail='Authentication Failed')
#     userRole_model = UserRole(**userRole_request.dict(), AssignedBy=user.get('id'), CreatedDate=get_time(), UpdatedDate=get_time())
#     db.add(userRole_model)
#     db.commit()
#     db.refresh(userRole_model)  # This ensures we get the generated ID
#     # Return the created lead with LeadId
#     return {"UserRoleId":userRole_model.UserRoleId }




@router.put("/update-user-roles/{userrole_id}", status_code=status.HTTP_204_NO_CONTENT )
async def update_users_roles (user: user_dependency,db: db_dependency,userrole_id: int, userroles_request:UsersRolesRequest):
    if user is None:
        raise HTTPException (status_code=401, detail='Authentication Failed')
    existing_ur = db.query(UserRole).filter(UserRole.UserRoleId == userrole_id).filter(UserRole.AssignedBy == user.get('id') ).first()
    if existing_ur is None:
        raise HTTPException (status_code=404, detail="user roles not found")
    existing_ur.UserId = userroles_request.UserId
    existing_ur.RoleId = userroles_request.RoleId
    existing_ur.IsActive = userroles_request.IsActive
    existing_ur.ExpiryDate = userroles_request.ExpiryDate
    existing_ur.Notes = userroles_request.Notes
    existing_ur.UpdatedDate = get_time()
    db.add(existing_ur)
    db.commit()



@router.delete("/delete-user-roles/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_roles (user: user_dependency, db: db_dependency, user_id : int =Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    roles_model = db.query(UserRole).filter(UserRole.UserRoleId== user_id).first()
    if  roles_model is None:
        raise HTTPException(status_code=404, detail="user roles not found")
    db.query(UserRole).filter(UserRole.UserRoleId == user_id).delete()
    db.commit()