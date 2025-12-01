from fastapi import APIRouter, Depends, HTTPException,status
from pytz import timezone
from fastapi import Path
from pydantic import BaseModel,Field
from models import AmenitySite
from typing import Annotated
from sqlalchemy.orm import Session,joinedload, load_only
from sqlalchemy import  select, func
from database import SessionLocal
from .auth import get_current_user
from datetime import datetime
from schemas.schemas import AmenitySiteRequest


router = APIRouter(
    prefix="/AmenitySite",
    tags = ['AmenitySite']
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
async def read_amentity_site(user:user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return db.query(AmenitySite).all()


@router.get('/getsingleAmenitysite/{amenitysite_id}', status_code=status.HTTP_200_OK)
async def read_amenity_site_by_id (user:user_dependency, db:db_dependency, amenitysite_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    amenitysite_model = db.query(AmenitySite).filter(AmenitySite.AmenitySiteId == amenitysite_id).first()
    if amenitysite_model is not None:
        return amenitysite_model
    raise HTTPException(status_code=404, detail= 'amenity site not found')


@router.post('/createamenitysite', status_code=status.HTTP_201_CREATED)
async def create_amenitysite(user: user_dependency, db:db_dependency, amenitysite_request:AmenitySiteRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    amenity_site = AmenitySite(
        AmenityId=amenitysite_request.AmenityId,
        SiteId=amenitysite_request.SiteId,
        AllotmentDate=amenitysite_request.AllotmentDate,
        IsActive=amenitysite_request.IsActive,
    )
    db.add(amenity_site)
    db.commit()
    if amenitysite_request is not None:
        return amenitysite_request
    raise HTTPException(status_code=404, detail='amenity site not found')


@router.put("/updateamenitysite/{amenitysite_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_amenity_site(user: user_dependency, db: db_dependency, amenitysite_id: int, amenitysite_request:AmenitySiteRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    amenity_exist = db.query(AmenitySite).filter(AmenitySite.AmenitySiteId == amenitysite_id ).first()
    if amenity_exist is None:
        raise HTTPException(status_code=404, detail="amenity site detail not found")
    amenity_exist.AmenityId=amenitysite_request.AmenityId
    amenity_exist.SiteId=amenitysite_request.SiteId
    amenity_exist.AllotmentDate=amenitysite_request.AllotmentDate
    amenity_exist.IsActive=amenitysite_request.IsActive
    db.add(amenity_exist)
    db.commit()


@router.delete("/deleteamenitysite/{amenitysite_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_amenitysite (user: user_dependency, db: db_dependency, amenitysite_id : int =Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    amenity_model = db.query(AmenitySite).filter(AmenitySite.AmenitySiteId == amenitysite_id).first()
    if amenity_model is None:
        raise HTTPException(status_code=404, detail="amenity site detail not found")
    db.query(AmenitySite).filter(AmenitySite.AmenitySiteId == amenitysite_id).delete()
    db.commit()