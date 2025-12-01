from fastapi import APIRouter, Depends, HTTPException,status
from pytz import timezone
from fastapi import Path
from pydantic import BaseModel,Field
from models import APIConfiguration
from typing import Annotated
from sqlalchemy.orm import Session,joinedload, load_only
from sqlalchemy import  select, func
from database import SessionLocal
from .auth import get_current_user
from datetime import datetime
from schemas.schemas import APIConfigurationBase


router = APIRouter(
    prefix="/APIConfiguration",
    tags = ['APIConfiguration']
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
async def read_api_Configuration(user:user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return db.query(APIConfiguration).all()



@router.post("/Create-API-Configuration", status_code=status.HTTP_201_CREATED)
async def create_api_configuration(user: user_dependency, db: db_dependency, apiconfiguration_request: APIConfigurationBase):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    api_model = APIConfiguration(**apiconfiguration_request.dict(), CreatedBy=user.get('id'), CreatedAt=get_time(), UpdatedAt=get_time())
    db.add(api_model)
    db.commit()
    db.refresh(api_model)  # This ensures we get the generated ID
    # Return the created lead with LeadId
    return {"ConfigId":api_model.ConfigId }



@router.delete("/delete-API-Configuration/{api_configuration_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_API_Configuration (user: user_dependency, db: db_dependency, api_configuration_id : int =Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    api_config_model = db.query(APIConfiguration).filter(APIConfiguration.ConfigId == api_configuration_id).first()
    if  api_config_model is None:
        raise HTTPException(status_code=404, detail="api configuration not found")
    db.query(APIConfiguration).filter(APIConfiguration.ConfigId == api_configuration_id).delete()
    db.commit()