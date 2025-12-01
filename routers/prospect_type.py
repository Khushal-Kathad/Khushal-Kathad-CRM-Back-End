from fastapi import APIRouter, Depends, HTTPException,status
from pytz import timezone
from fastapi import Path
from pydantic import BaseModel,Field
from models import Lead,Contact, ProspectType, Site
from typing import Annotated
from sqlalchemy.orm import Session,joinedload, load_only
from sqlalchemy import  select, func
from database import SessionLocal
from .auth import get_current_user
from datetime import datetime
from schemas.schemas import ProspectTypeRequest


router = APIRouter(
    prefix="/prospect",
    tags = ['prospect']
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


@router.get("/")
async def read_prospect_type(user:user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException (status_code=401, detail='Authentication Failed')
    return db.query(ProspectType).all()



@router.get("/getsingleprospect_type/{prospect_id}", status_code=status.HTTP_200_OK )
async def read_prospect (user:user_dependency, db: db_dependency, prospect_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException (status_code=401, detail='Authentication Failed')
    prospect_model = db.query(ProspectType).filter(ProspectType.ProspectTypeId ==prospect_id).first()
    if prospect_model is not None:
        return prospect_model
    raise HTTPException(status_code=404, detail = 'prospect type not found')



@router.post("/createprospect",status_code=status.HTTP_201_CREATED)
async def create_prospect(user: user_dependency, db: db_dependency,
                       prospect_request:ProspectTypeRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    new_prospect = ProspectType(
        ProspectTypeName = prospect_request.ProspectTypeName
    )
    db.add(new_prospect)
    db.commit()
    db.refresh(new_prospect)
    return new_prospect



@router.put("/updateprospect/{prospect_id}", status_code=status.HTTP_204_NO_CONTENT )
async def update_prospect (user: user_dependency,db: db_dependency , prospect_id: int, prospect_request:ProspectTypeRequest):
    if user is None:
        raise HTTPException (status_code=401, detail='Authentication Failed')
    existing_prospect = db.query(ProspectType).filter(ProspectType.ProspectTypeId == prospect_id).first()
    if existing_prospect is None:
        raise HTTPException (status_code=404, detail="prospect not found")
    existing_prospect.ProspectTypeName = prospect_request.ProspectTypeName
    db.add(existing_prospect)
    db.commit()


@router.delete("/deleteprospect/{prospect_id}", status_code=status.HTTP_204_NO_CONTENT )
async def delete_prospect (user:user_dependency, db: db_dependency, prospect_id : int =Path(gt=0)):
    if user is None:
        raise HTTPException (status_code=401, detail='Authentication Failed')
    prospect_model = db.query(ProspectType).filter(ProspectType.ProspectTypeId == prospect_id).first()
    if prospect_model is None:
        raise HTTPException (status_code=404, detail="prospect not found")
    db.query(ProspectType).filter(ProspectType.ProspectTypeId == prospect_id).delete()
    db.commit()
