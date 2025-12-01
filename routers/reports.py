from fastapi import APIRouter, Depends, HTTPException,status
from pytz import timezone
from fastapi import Path
from pydantic import BaseModel,Field
from models import Reports
from typing import Annotated
from sqlalchemy.orm import Session,joinedload, load_only
from sqlalchemy import  select, func
from database import SessionLocal
from .auth import get_current_user
from datetime import datetime
from schemas.schemas import ReportsRequest


router = APIRouter(
    prefix="/reports",
    tags = ['reports']
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
async def read_reports(user:user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return db.query(Reports).all()


@router.get('/getsinglereports/{report_id}', status_code=status.HTTP_200_OK)
async def read_report_by_id (user:user_dependency, db:db_dependency, report_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    report_model = db.query(Reports).filter(Reports.ReportId == report_id).first()
    if report_model is not None:
        return report_model
    raise HTTPException(status_code=404, detail= 'reports not found')


@router.post("/CreateReports", status_code=status.HTTP_201_CREATED)
async def create_Reports(user: user_dependency, db: db_dependency, reports_request: ReportsRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    reports_model = Reports(**reports_request.dict(), CreatedById=user.get('id'), CreatedDate=get_time(), UpdatedDate=get_time())
    db.add(reports_model)
    db.commit()
    db.refresh(reports_model)  # This ensures we get the generated ID
    # Return the created lead with LeadId
    return {"ReportId":reports_model.ReportId }


@router.put("/updatereports/{report_id}", status_code=status.HTTP_204_NO_CONTENT )
async def update_reports (user: user_dependency,db: db_dependency,report_id: int, reports_request:ReportsRequest):
    if user is None:
        raise HTTPException (status_code=401, detail='Authentication Failed')
    existing_reports = db.query(Reports).filter(Reports.ReportId == report_id).filter(Reports.CreatedById == user.get('id') ).first()
    if existing_reports is None:
        raise HTTPException (status_code=404, detail="Reports not found")
    existing_reports.ReportName = reports_request.ReportName
    existing_reports.ReportFrequency = reports_request.ReportFrequency
    existing_reports.DeliveryMethods = reports_request.DeliveryMethods
    existing_reports.RecipientUserId = reports_request.RecipientUserId
    existing_reports.PublishingDateTime = reports_request.PublishingDateTime
    existing_reports.IsActive = reports_request.IsActive
    existing_reports.UpdatedDate = get_time()
    db.add(existing_reports)
    db.commit()


@router.delete("/deletereports/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reports (user: user_dependency, db: db_dependency, report_id : int =Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    report_model = db.query(Reports).filter(Reports.ReportId == report_id).first()
    if  report_model is None:
        raise HTTPException(status_code=404, detail="Reports not found")
    db.query(Reports).filter(Reports.ReportId == report_id).delete()
    db.commit()