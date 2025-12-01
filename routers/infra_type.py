# from string import ascii_uppercase
#
# from fastapi import APIRouter, Depends, HTTPException,status
# from pytz import timezone
# from fastapi import Path
# from pydantic import BaseModel,Field
# from models import InfraType
# from typing import Annotated
# from sqlalchemy.orm import Session,joinedload, load_only
# from sqlalchemy import  select, func
# from database import SessionLocal
# from .auth import get_current_user
# from datetime import datetime
# from schemas.schemas import InfraTypeRequest
#
#
# router = APIRouter(
#     prefix="/infra_type",
#     tags = ['infra_type']
# )
#
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
#
#
# def get_time():
#     ind_time = datetime.now(timezone("Asia/Kolkata"))
#     return ind_time
#
# db_dependency = Annotated[Session, Depends(get_db)]
# user_dependency = Annotated[dict, Depends(get_current_user)]
#
#
# @router.get('/')
# async def read_infra_type(user:user_dependency, db: db_dependency):
#     if user is None:
#         raise HTTPException(status_code=401, detail="Authentication Failed")
#     return db.query(InfraType).all()
#
#
#
#
# @router.get('/getsingleinfratype/{infra_type_id}', status_code=status.HTTP_200_OK)
# async def read_infra_type_by_id (user:user_dependency, db:db_dependency, infra_type_id: int = Path(gt=0)):
#     if user is None:
#         raise HTTPException(status_code=401, detail='Authentication Failed')
#     infra_type_model = db.query(InfraType).filter(InfraType.InfraTypeid == infra_type_id).first()
#     if infra_type_model is not None:
#         return infra_type_model
#     raise HTTPException(status_code=404, detail= 'infra type not found')
#
#
#
#
# @router.post('/createinfra_type', status_code=status.HTTP_201_CREATED)
# async def create_infra_type(user: user_dependency, db:db_dependency, infratype_request:InfraTypeRequest):
#     if user is None:
#         raise HTTPException(status_code=401, detail='Authentication Failed')
#     new_infra_type = InfraType(
#         InfraTypeName=infratype_request.InfraTypeName
#     )
#     db.add(new_infra_type)
#     db.commit()
#     if new_infra_type is not  None:
#         return new_infra_type
#     raise HTTPException(status_code=404, detail='infra type not found')
#
#
#
#
# @router.put("/updateinfratype/{infra_type_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def update_infra_type(user: user_dependency, db: db_dependency, infra_type_id: int, infratype_request:InfraTypeRequest):
#     if user is None:
#         raise HTTPException(status_code=401, detail='Authentication Failed')
#     infra_type_exist = db.query(InfraType).filter(InfraType.InfraTypeid == infra_type_id ).first()
#     if infra_type_exist is None:
#         raise HTTPException(status_code=404, detail="infra type not found")
#     infra_type_exist.InfraTypeName=infratype_request.InfraTypeName
#     db.add(infra_type_exist)
#     db.commit()
#
#
#
# @router.delete("/deleteinfratype/{infra_type_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_infra_type (user: user_dependency, db: db_dependency, infra_type_id : int =Path(gt=0)):
#     if user is None:
#         raise HTTPException(status_code=401, detail='Authentication Failed')
#     infra_type_model = db.query(InfraType).filter(InfraType.InfraTypeid == infra_type_id).first()
#     if infra_type_model is None:
#         raise HTTPException(status_code=404, detail="infra type not found")
#     db.query(InfraType).filter(InfraType.InfraTypeid == infra_type_id).delete()
#     db.commit()