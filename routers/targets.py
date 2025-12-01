from string import ascii_uppercase
from fastapi import APIRouter, Depends, HTTPException,status
from pytz import timezone
from fastapi import Path
from pydantic import BaseModel,Field
# from models import Lead, Contact, ProspectType, Site
from typing import Annotated
from sqlalchemy.orm import Session,joinedload, load_only
from sqlalchemy import  select, func
from database import SessionLocal
from models import Targets
from .auth import get_current_user
from datetime import datetime
from schemas.schemas import TargetsRequest


router = APIRouter(
    prefix="/targets",
    tags = ['targets']
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
async def read_targets(user:user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return db.query(Targets).all()




@router.get('/get_single_targets/{targets_id}', status_code=status.HTTP_200_OK)
async def read_targets_by_id (user:user_dependency, db:db_dependency, targets_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    targets_item_model = db.query(Targets).filter(Targets.TargetId == targets_id).first()
    if targets_item_model is not None:
        return targets_item_model
    raise HTTPException(status_code=404, detail= 'targets item not found')





@router.post('/create_targets', status_code=status.HTTP_201_CREATED)
async def create_targets(user: user_dependency, db:db_dependency, targets_request:TargetsRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    new_targets = Targets(
        TargetType = targets_request.TargetType,
        TargetDescription = targets_request.TargetDescription,
        # TargetStartDate = targets_request.TargetStartDate,
        TargetStartDate = get_time(),
        # TargetEndDate = targets_request.TargetEndDate
        TargetEndDate = get_time(),
        TargetValue = targets_request.TargetValue,
        EvaluationCycle = targets_request.EvaluationCycle,
        EvaluationDate = targets_request.EvaluationDate,
        Is_Active = targets_request.Is_Active,
        CreatedDate = targets_request.CreatedDate,
        UpdatedDate = targets_request.UpdatedDate,
        CreatedById = targets_request.CreatedById

    )
    db.add(new_targets)
    db.commit()
    if new_targets is not  None:
        return new_targets
    raise HTTPException(status_code=404, detail='target not found')





@router.put("/update_targets/{targets_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_targets(user: user_dependency, db: db_dependency, targets_id: int, targets_request:TargetsRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    targets_exist = db.query(Targets).filter(Targets.TargetId == targets_id ).first()
    if targets_exist is None:
        raise HTTPException(status_code=404, detail="action item not found")
    targets_exist.TargetType = targets_request.TargetType
    targets_exist.TargetDescription = targets_request.TargetDescription
    targets_exist.TargetStartDate = targets_request.TargetStartDate
    targets_exist.TargetEndDate = targets_request.TargetEndDate
    targets_exist.TargetValue = targets_request.TargetValue
    targets_exist.EvaluationCycle = targets_request.EvaluationCycle
    targets_exist.EvaluationDate = targets_request.EvaluationDate
    targets_exist.Is_Active = targets_request.Is_Active
    targets_exist.CreatedDate = targets_request.CreatedDate
    targets_exist.UpdatedDate = targets_request.UpdatedDate
    targets_exist.CreatedById = targets_request.CreatedById

    db.add(targets_exist)
    db.commit()





@router.delete("/delete_targets/{targets_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_targets (user: user_dependency, db: db_dependency, targets_id : int =Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    action_item_model = db.query(Targets).filter(Targets.TargetId == targets_id ).first()
    if action_item_model is None:
        raise HTTPException(status_code=404, detail="Target not found")
    db.query(Targets).filter(Targets.TargetId == targets_id).delete()
    db.commit()