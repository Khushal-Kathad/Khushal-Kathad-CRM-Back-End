from fastapi import APIRouter, Depends, HTTPException,status
from pytz import timezone
from fastapi import Path
from pydantic import BaseModel,Field
from models import PermissionFilterValue
from typing import Annotated
from sqlalchemy.orm import Session,joinedload, load_only
from sqlalchemy import  select, func
from database import SessionLocal
from .auth import get_current_user
from datetime import datetime
from schemas.schemas import PermissionFiltersValuesRequest


router = APIRouter(
    prefix="/PermissionFilterValues",
    tags = ['PermissionFilterValues']
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
async def read_PermissionFilterValues(user:user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return db.query(PermissionFilterValue).all()


@router.get('/get-single-Permission-Filter-Values/{permission_id}', status_code=status.HTTP_200_OK)
async def Read_Permission_Filter_Values_by_id(user:user_dependency, db: db_dependency, permission_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    permission_model = db.query(PermissionFilterValue).filter(PermissionFilterValue.ValueId == permission_id).first()
    if permission_model is not None:
        return permission_model
    raise HTTPException(status_code=404, detail=' Permission Filter values not found')




@router.post("/Create-Permission-Filter-Values", status_code=status.HTTP_201_CREATED)
async def create_Permission_Filter_Values(user: user_dependency, db: db_dependency, Permission_request: PermissionFiltersValuesRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    Permission_model = PermissionFilterValue(**Permission_request.dict())
    db.add( Permission_model)
    db.commit()
    db.refresh( Permission_model)  # This ensures we get the generated ID
    # Return the created lead with LeadId
    return {"Permission-Filter-Values-id":Permission_model.ValueId }


# @router.put("/update_Roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT )
# async def update_Roles (user: user_dependency,db: db_dependency,role_id: int, roles_request:RolesRequest):
#     if user is None:
#         raise HTTPException (status_code=401, detail='Authentication Failed')
#     existing_role = db.query(Role).filter(Role.RoleId == role_id).filter(Role.CreatedBy == user.get('id') ).first()
#     if existing_role is None:
#         raise HTTPException (status_code=404, detail=" roles not found")
#     existing_role.Name = roles_request.Name
#     existing_role.Description = roles_request.Description
#     existing_role.IsSystem = roles_request.IsSystemRole
#     existing_role.Active = roles_request.Active
#     existing_role.HierarchyLevel = roles_request.HierarchyLevel
#     existing_role.UpdatedDate = get_time()
#     db.add(existing_role)
#     db.commit()



@router.delete("/delete-Permission-Filter-Values/{Permission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_Permission_Filter_Values (user: user_dependency, db: db_dependency, Permission_id : int =Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    Permission_model = db.query(PermissionFilterValue).filter(PermissionFilterValue.ValueId == Permission_id).first()
    if  Permission_model is None:
        raise HTTPException(status_code=404, detail=" Permission filter Values not found")
    db.query(PermissionFilterValue).filter(PermissionFilterValue.ValueId == Permission_id).delete()
    db.commit()