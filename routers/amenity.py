from fastapi import APIRouter, Depends, HTTPException,status
from pytz import timezone
from fastapi import Path
from pydantic import BaseModel,Field
from models import Amenity
from typing import Annotated
from sqlalchemy.orm import Session,joinedload, load_only
from sqlalchemy import  select, func
from database import SessionLocal
from .auth import get_current_user
from datetime import datetime
from schemas.schemas import AmenityRequest


router = APIRouter(
    prefix="/amenity",
    tags = ['amenity']
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
async def read_amenity(user:user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return db.query(Amenity).all()




@router.get('/getsingleamenity/{amenity_id}', status_code=status.HTTP_200_OK)
async def read_amenity_by_id (user:user_dependency, db:db_dependency, amenity_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    amenity_model = db.query(Amenity).filter(Amenity.AmenityId == amenity_id).first()
    if amenity_model is not None:
        return amenity_model
    raise HTTPException(status_code=404, detail= 'amenity not found')




@router.post('/createamenity', status_code=status.HTTP_201_CREATED)
async def create_amenity(user: user_dependency, db:db_dependency, amenity_request:AmenityRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    new_amenity = Amenity(
        AmenityName=amenity_request.AmenityName
    )
    db.add(new_amenity)
    db.commit()
    db.refresh(new_amenity)
    return new_amenity




@router.put("/updateamenity/{amenity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_amenity(user: user_dependency, db: db_dependency, amenity_id: int, amenity_request: AmenityRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    amenity_exist = db.query(Amenity).filter(Amenity.AmenityId == amenity_id ).first()
    if amenity_exist is None:
        raise HTTPException(status_code=404, detail="amenity  not found")
    amenity_exist.AmenityName=amenity_request.AmenityName
    db.add(amenity_exist)
    db.commit()



@router.delete("/deleteamenity/{amenity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_amenity (user: user_dependency, db: db_dependency, amenity_id : int =Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    amenity_model = db.query(Amenity).filter(Amenity.AmenityId == amenity_id).first()
    if amenity_model is None:
        raise HTTPException(status_code=404, detail="Amenity not found")
    db.query(Amenity).filter(Amenity.AmenityId == amenity_id).delete()
    db.commit()