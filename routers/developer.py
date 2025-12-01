from fastapi import APIRouter, Depends, HTTPException,status
from pytz import timezone
from fastapi import Path
from pydantic import BaseModel,Field
from models import Developer
from typing import Annotated
from sqlalchemy.orm import Session,joinedload, load_only
from sqlalchemy import  select, func
from database import SessionLocal
from .auth import get_current_user
from datetime import datetime
from schemas.schemas import DeveloperRequest


router = APIRouter(
    prefix="/developer",
    tags = ['developer']
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
async def read_developer(user:user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return db.query(Developer).all()


@router.get('/getsinglesitedeveloper/{developer_id}', status_code=status.HTTP_200_OK)
async def read_developer_by_id (user:user_dependency, db:db_dependency, developer_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    developer_model = db.query(Developer).filter(Developer.DeveloperId == developer_id).first()
    if developer_model is not None:
        return developer_model
    raise HTTPException(status_code=404, detail= 'developer not found')



@router.post('/createdeveloper', status_code=status.HTTP_201_CREATED)
async def create_developer(user: user_dependency, db:db_dependency, developer_request:DeveloperRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    developer = Developer(
        DeveloperName=developer_request.DeveloperName,
        DeveloperEmail=developer_request.DeveloperEmail,
        DeveloperPhone=developer_request.DeveloperPhone,
        DeveloperAddress=developer_request.DeveloperAddress,
        DeveloperCity=developer_request.DeveloperCity,
        DeveloperState=developer_request.DeveloperState,
        DeveloperPostalCode=developer_request.DeveloperPostalCode,
        IsActive=developer_request.IsActive,
        CreatedDate=developer_request.CreatedDate,
        UpdatedDate=developer_request.UpdatedDate,
        CreatedById=developer_request.CreatedById,
    )
    db.add(developer)
    db.commit()
    if developer_request is not None:
        return developer_request
    raise HTTPException(status_code=404, detail='developer not found')



@router.put("/updatedeveloper/{dev_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_developer(user: user_dependency, db: db_dependency, dev_id: int, developer_request:DeveloperRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    dev_exist = db.query(Developer).filter(Developer.DeveloperId == dev_id ).first()
    if dev_exist is None:
        raise HTTPException(status_code=404, detail="developer not found")
    dev_exist.DeveloperName=developer_request.DeveloperName
    dev_exist.DeveloperEmail=developer_request.DeveloperEmail
    dev_exist.DeveloperPhone=developer_request.DeveloperPhone
    dev_exist.DeveloperAddress=developer_request.DeveloperAddress
    dev_exist.DeveloperCity=developer_request.DeveloperCity
    dev_exist.DeveloperState=developer_request.DeveloperState
    dev_exist.DeveloperPostalCode=developer_request.DeveloperPostalCode
    dev_exist.IsActive=developer_request.IsActive
    dev_exist.CreatedDate=developer_request.CreatedDate
    dev_exist.UpdatedDate=developer_request.UpdatedDate
    dev_exist.CreatedById=developer_request.CreatedById
    db.add(dev_exist)
    db.commit()


@router.delete("/deletedeveloper/{dev_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_developer (user: user_dependency, db: db_dependency, dev_id : int =Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    dev_model = db.query(Developer).filter(Developer.DeveloperId == dev_id).first()
    if dev_model is None:
        raise HTTPException(status_code=404, detail="developer detail not found")
    db.query(Developer).filter(Developer.DeveloperId == dev_id).delete()
    db.commit()