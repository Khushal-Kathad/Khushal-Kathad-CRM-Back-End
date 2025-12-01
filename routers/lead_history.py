from fastapi import APIRouter, Depends, HTTPException,status
from pytz import timezone
from fastapi import Path
from pydantic import BaseModel,Field
from models import  Contact, ProspectType, Site, LeadHistory
from typing import Annotated
from sqlalchemy.orm import Session,joinedload, load_only
from sqlalchemy import  select, func
from database import SessionLocal
from .auth import get_current_user
from datetime import datetime
from schemas.schemas import LeadHistoryRequest


router = APIRouter(
    prefix="/lead_history",
    tags = ['lead_history']
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
async def read_lead_history(user:user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return db.query(LeadHistory).all()




@router.get('/get_single_lead_history/{lead_history_id}', status_code=status.HTTP_200_OK)
async def read_lead_history_by_id (user:user_dependency, db:db_dependency, lead_history_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    lead_history_model = db.query(LeadHistory).filter(LeadHistory.LeadHistoryId == lead_history_id).first()
    if lead_history_model is not None:
        return lead_history_model
    raise HTTPException(status_code=404, detail= 'Lead History not found')





@router.post('/create_lead_history', status_code=status.HTTP_201_CREATED)
async def create_lead_history(user: user_dependency, db:db_dependency, leadHistory_request:LeadHistoryRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    new_lead_history = LeadHistory(
        LeadId=leadHistory_request.LeadId,
        UpdateName=leadHistory_request.UpdateName,
        UpdateDetails=leadHistory_request.UpdateDetails
    )
    db.add(new_lead_history)
    db.commit()
    if new_lead_history is not  None:
        return new_lead_history
    raise HTTPException(status_code=404, detail='Lead History not found')





@router.put("/update_lead_history/{lead_history_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_lead_history(user: user_dependency, db: db_dependency, lead_history_id: int, leadHistory_request:LeadHistoryRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    leadHistory_exist = db.query(LeadHistory).filter(LeadHistory.LeadHistoryId == lead_history_id).first()
    if leadHistory_exist is None:
        raise HTTPException(status_code=404, detail="Lead History not found")
    leadHistory_exist.LeadId=leadHistory_request.LeadId
    leadHistory_exist.UpdateName = leadHistory_request.UpdateName
    leadHistory_exist.UpdateDetails = leadHistory_request.UpdateDetails
    db.add(leadHistory_exist)
    db.commit()





@router.delete("/delete_lead_history/{lead_history_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lead_history (user: user_dependency, db: db_dependency, lead_history_id : int =Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    lead_history_model = db.query(LeadHistory).filter(LeadHistory.LeadHistoryId == lead_history_id).first()
    if lead_history_model is None:
        raise HTTPException(status_code=404, detail="Lead History not found")
    db.query(LeadHistory).filter(LeadHistory.LeadHistoryId == lead_history_id).delete()
    db.commit()