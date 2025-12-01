from fastapi import APIRouter, Depends, HTTPException,status
from pytz import timezone
from fastapi import Path
from pydantic import BaseModel,Field
from models import UserTargetAllotment
from typing import Annotated
from sqlalchemy.orm import Session,joinedload, load_only
from sqlalchemy import  select, func
from database import SessionLocal
from .auth import get_current_user
from datetime import datetime
from schemas.schemas import UserTargetAllotmentRequest


router = APIRouter(
    prefix="/user_target_allotment",
    tags = ['user_target_allotment']
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
async def read_user_target_allotment(user:user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return db.query(UserTargetAllotment).all()


@router.get('/getsingleusertargetallotment/{user_target_allotment_id}', status_code=status.HTTP_200_OK)
async def read_user_target_allotment_by_id (user:user_dependency, db:db_dependency, user_target_allotment_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    user_target_allotment_model = db.query(UserTargetAllotment).filter(UserTargetAllotment.AllotmentId == user_target_allotment_id).first()
    if user_target_allotment_model is not None:
        return user_target_allotment_model
    raise HTTPException(status_code=404, detail= 'user target allotment not found')


@router.post('/createusertagretallotment', status_code=status.HTTP_201_CREATED)
async def create_user_target_allotment(user: user_dependency, db:db_dependency, user_target_allotment_request:UserTargetAllotmentRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    user_target_allotment = UserTargetAllotment(
        AllotedToUserId = user_target_allotment_request.AllotedToUserId,
        TargetId = user_target_allotment_request.TargetId,
        AllottedValue = user_target_allotment_request.AllottedValue,
        AchievedValue = user_target_allotment_request.AchievedValue,
        AllotmentStatus = user_target_allotment_request.AllotmentStatus,
        AllotmentDate = user_target_allotment_request.AllotmentDate,
        CompletionDate = user_target_allotment_request.CompletionDate,
        Remarks = user_target_allotment_request.Remarks,
        CreatedDate = user_target_allotment_request.CreatedDate,
        UpdatedDate = user_target_allotment_request.UpdatedDate
    )
    db.add(user_target_allotment)
    db.commit()
    if user_target_allotment_request is not None:
        return user_target_allotment_request
    raise HTTPException(status_code=404, detail='user target allotment not found')


@router.put("/updateusertargetallotment/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_user_target_allotment(user: user_dependency, db: db_dependency, user_id: int, user_target_allotment_request:UserTargetAllotmentRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    user_exist = db.query(UserTargetAllotment).filter(UserTargetAllotment.AllotmentId == user_id ).first()
    if user_exist is None:
        raise HTTPException(status_code=404, detail="user target allotment not found")
    user_exist.AllotedToUserId = user_target_allotment_request.AllotedToUserId
    user_exist.TargetId = user_target_allotment_request.TargetId
    user_exist.AllottedValue = user_target_allotment_request.AllottedValue
    user_exist.AchievedValue = user_target_allotment_request.AchievedValue
    user_exist.AllotmentStatus = user_target_allotment_request.AllotmentStatus
    user_exist.AllotmentDate = user_target_allotment_request.AllotmentDate
    user_exist.CompletionDate = user_target_allotment_request.CompletionDate
    user_exist.Remarks = user_target_allotment_request.Remarks
    user_exist.UpdatedDate = user_target_allotment_request.UpdatedDate
    db.add(user_exist)
    db.commit()


@router.delete("/deleteusertargetallotment/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_target_allotment (user: user_dependency, db: db_dependency, user_id : int =Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    user_model = db.query(UserTargetAllotment).filter(UserTargetAllotment.AllotmentId == user_id).first()
    if user_model is None:
        raise HTTPException(status_code=404, detail="user target allotment not found")
    db.query(UserTargetAllotment).filter(UserTargetAllotment.AllotmentId == user_id).delete()
    db.commit()



