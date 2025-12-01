from string import ascii_uppercase
from dns.e164 import query
from fastapi import APIRouter, Depends, HTTPException,status
from pytz import timezone
from fastapi import Path
from pydantic import BaseModel,Field
# from models import Lead, Contact, ProspectType, Site
from typing import Annotated
from sqlalchemy.orm import Session,joinedload, load_only
from sqlalchemy import  select, func
from database import SessionLocal
from models import Targets, Lead
from .auth import get_current_user
from datetime import datetime, timedelta
from schemas.schemas import TargetsRequest
from sqlalchemy import cast, Date
from datetime import datetime, timedelta




router = APIRouter(
    prefix="/home_api",
    tags = ['home_api']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# def get_time():
#     ind_time = datetime.now(timezone("Asia/Kolkata"))
#     return ind_time

def get_date():
    ind_date = datetime.now(timezone("Asia/Kolkata")).date()
    return ind_date

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]






@router.get('/')
async def monthly_targets(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    try:
        today = datetime.now().date()
        month_start_date = today.replace(day=1)
        next_month = (today.month % 12) + 1
        next_year = today.year + (1 if today.month == 12 else 0)
        month_end_date = datetime(next_year, next_month, 1).date() - timedelta(days=1)
    except ValueError:
        raise HTTPException(status_code=400, detail="Error calculating month start and end dates")
    query = db.query(Targets).filter(Targets.TargetId == user.get('id'),
        Targets.TargetType == 'count',
        Targets.TargetStartDate >= month_start_date,
        Targets.TargetEndDate <= month_end_date)
    # results = query.all()
    # return {"targetNO": [target.TargetNo for target in results]}
    results = query.all()
    if not results:  # If no matching targets, return [0]
        return {"targetNO": [0]}
    return {"targetNO": [target.TargetNo for target in results]}







# @router.get('/monthly_conversions')
# async def monthly_conversions(user: user_dependency, db: db_dependency):
#     if user is None:
#          raise HTTPException(status_code=401, detail="Authentication Failed")
#     try:
#         today = datetime.now().date()
#         month_start_date = today.replace(day=1)
#         print(month_start_date)
#         next_month = (today.month % 12) + 1
#         next_year = today.year + (1 if today.month == 12 else 0)
#         month_end_date = datetime(next_year, next_month, 1).date() - timedelta(days=1)
#         print(month_end_date)
#     except ValueError:
#         raise HTTPException(status_code=400, detail="Error calculating month start and end dates")
#     win_count = db.query(Lead).filter(Lead.LeadCreatedById == user.get('id'),
#                 Lead.LeadCreatedDate >= month_start_date,
#                 Lead.LeadClosedDate <= month_end_date,
#                 Lead.LeadStatus == 'Win').count()
#     return {"win_count": win_count}



@router.get('/monthly_conversions')
async def monthly_conversions(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    try:
        today = datetime.now().date()
        month_start_date = today.replace(day=1)
        next_month = (today.month % 12) + 1
        next_year = today.year + (1 if today.month == 12 else 0)
        month_end_date = datetime(next_year, next_month, 1).date() - timedelta(days=1)
    except ValueError:
        raise HTTPException(status_code=400, detail="Error calculating month start and end dates")
    win_count = db.query(Lead).filter(
        Lead.CreatedById == user.get('id'),
        Lead.CreatedDate >= month_start_date,
        Lead.LeadClosedDate <= month_end_date,
        Lead.LeadStatus == 'Win'
    ).count()
    target_query = db.query(Targets).filter(
        Targets.TargetId == user.get('id'),
        Targets.TargetType == 'count',
        Targets.TargetStartDate >= month_start_date,
        Targets.TargetEndDate <= month_end_date
    )
    targets = target_query.all()
    target_numbers = [target.TargetNo for target in targets]
    total_target = sum(target_numbers)
    if total_target == 0:
        target_rate = 0.0
    else:
        target_rate = (win_count / total_target) * 100

    return {
        "win_count": win_count,
        "target_rate": target_rate
    }




@router.get('/overall_conversion_rate')
async def overall_conversion_rate(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    user_id = user.get('id')
    total_leads = db.query(Lead).filter(Lead.CreatedById == user_id).count()
    wins = db.query(Lead).filter(Lead.CreatedById == user_id,Lead.LeadStatus == 'Win').count()
    if total_leads > 0 :
        win_percentage = (wins / total_leads) * 100
    else:
        win_percentage = 0.0
    return { 'overall_conversion_rate': win_percentage }

