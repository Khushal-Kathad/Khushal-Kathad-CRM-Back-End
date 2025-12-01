from fastapi import APIRouter, Depends, HTTPException,status
from pytz import timezone
from fastapi import Path
from pydantic import BaseModel,Field
from models import NotificationConfiguration
from typing import Annotated
from sqlalchemy.orm import Session,joinedload, load_only
from sqlalchemy import  select, func
from database import SessionLocal
from .auth import get_current_user
from datetime import datetime
from schemas.schemas import NotificationConfigurationBase


router = APIRouter(
    prefix="/NotificationConfiguration",
    tags = ['NotificationConfiguration']
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
async def read_notification_configuration(user:user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return db.query(NotificationConfiguration).all()



@router.post("/Create-notification-configuration", status_code=status.HTTP_201_CREATED)
async def create_notification_configuration(user: user_dependency, db: db_dependency, notification_configuration_request: NotificationConfigurationBase):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    notification_model = NotificationConfiguration(**notification_configuration_request.dict(), CreatedById=user.get('id'), CreatedAt=get_time(), UpdatedAt=get_time())
    db.add(notification_model)
    db.commit()
    db.refresh(notification_model)  # This ensures we get the generated ID
    # Return the created lead with LeadId
    return {"NotificationId":notification_model.NotificationId }