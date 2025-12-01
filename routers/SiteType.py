from fastapi import APIRouter, Depends, HTTPException,status
from pytz import timezone
from fastapi import Path
from pydantic import BaseModel,Field
from models import SiteType
from typing import Annotated
from sqlalchemy.orm import Session,joinedload, load_only
from sqlalchemy import  select, func
from database import SessionLocal
from .auth import get_current_user
from datetime import datetime
from schemas.schemas import SiteTypeRequest


router = APIRouter(
    prefix="/SiteType",
    tags = ['SiteType']
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
async def read_Site_type(user:user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return db.query(SiteType).all()


@router.get('/getsinglesitetype/{site_id}', status_code=status.HTTP_200_OK)
async def read_site_type_by_id (user:user_dependency, db:db_dependency, site_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    site_model = db.query(SiteType).filter(SiteType.SiteTypeId == site_id).first()
    if site_model is not None:
        return site_model
    raise HTTPException(status_code=404, detail= 'site type not found')


@router.post('/createsitetype', status_code=status.HTTP_201_CREATED)
async def create_site_type(user: user_dependency, db:db_dependency, site_request:SiteTypeRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    site_type = SiteType(
        SiteType=site_request.SiteType
    )
    db.add(site_type)
    db.commit()
    db.refresh(site_type)
    return site_type


@router.put("/updatesitetype/{site_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_sitetype(user: user_dependency, db: db_dependency, site_id: int, site_request:SiteTypeRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    site_exist = db.query(SiteType).filter(SiteType.SiteTypeId == site_id ).first()
    if site_exist is None:
        raise HTTPException(status_code=404, detail="site type detail not found")
    site_exist.SiteType=site_request.SiteType
    db.add(site_exist)
    db.commit()


@router.delete("/deletesitetype/{site_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_site_type (user: user_dependency, db: db_dependency, site_id : int =Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    site_model = db.query(SiteType).filter(SiteType.SiteTypeId == site_id).first()
    if site_model is None:
        raise HTTPException(status_code=404, detail="site type detail not found")
    db.query(SiteType).filter(SiteType.SiteTypeId == site_id).delete()
    db.commit()