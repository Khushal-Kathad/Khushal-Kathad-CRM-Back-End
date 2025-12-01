from fastapi import APIRouter, Depends, HTTPException,status
from pytz import timezone
from fastapi import Path
from pydantic import BaseModel,Field
from models import LeaveApplication
from typing import Annotated
from sqlalchemy.orm import Session,joinedload, load_only
from sqlalchemy import  select, func
from database import SessionLocal
from .auth import get_current_user
from datetime import datetime
from schemas.schemas import LeavesRequest


router = APIRouter(
    prefix="/LeaveApplication",
    tags = ['LeaveApplication']
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
async def read_leave_application(user:user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return db.query(LeaveApplication).all()


@router.get('/getsingleleaveapplication/{leave_id}', status_code=status.HTTP_200_OK)
async def read_leave_application_by_id (user:user_dependency, db:db_dependency, leave_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    leave_model = db.query(LeaveApplication).filter(LeaveApplication.LeaveApplicationId == leave_id).first()
    if leave_model is not None:
        return leave_model
    raise HTTPException(status_code=404, detail= 'leave application not found')




@router.post('/createleaveapplication', status_code=status.HTTP_201_CREATED)
async def create_leave_application(user: user_dependency, db:db_dependency, leave_request:LeavesRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    leave_application = LeaveApplication(**leave_request.dict(), CreatedById=user.get('id'), CreatedDate=get_time(), UpdatedDate=get_time())
    db.add(leave_application)
    db.commit()
    db.refresh(leave_application)
    return {"LeaveApplicationId" : leave_application.LeaveApplicationId}




@router.put("/updateleaveapplication/{leave_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_leave_application(user: user_dependency, db: db_dependency, leave_id: int, leave_request:LeavesRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    leave_exist = db.query(LeaveApplication).filter(LeaveApplication.LeaveApplicationId == leave_id).first()
    if leave_exist is None:
        raise HTTPException(status_code=404, detail="leave application detail not found")
    leave_exist.EmployeeId=leave_request.EmployeeId
    leave_exist.LeaveType=leave_request.LeaveType
    leave_exist.StartDate=leave_request.StartDate
    leave_exist.EndDate=leave_request.EndDate
    leave_exist.Status=leave_request.Status
    if leave_request.BackupEmployeeId is not None:
        leave_exist.BackupEmployeeId=leave_request.BackupEmployeeId
    if leave_request.AutoReassign is not None:
        leave_exist.AutoReassign=leave_request.AutoReassign
    if leave_request.Notes is not None:
        leave_exist.Notes=leave_request.Notes
    # leave_exist.CreatedDate=leave_request.CreatedDate
    leave_exist.UpdatedDate=get_time()
    # visitors_model.UpdatedDate = get_time()
    # leave_exist.CreatedById=leave_request.CreatedById
    db.add(leave_exist)
    db.commit()


@router.delete("/deleteleaveapplication/{leave_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_leave_application (user: user_dependency, db: db_dependency, leave_id : int =Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    leave_model = db.query(LeaveApplication).filter(LeaveApplication.LeaveApplicationId == leave_id).first()
    if leave_model is None:
        raise HTTPException(status_code=404, detail="leave application detail not found")
    # db.query(Account).filter(Account.AccountId == account_id).delete()
    db.query(LeaveApplication).filter(LeaveApplication.LeaveApplicationId == leave_id).delete()
    db.commit()



@router.get('/Total-leave-Request')
async def Total_leave_Request(user:user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
        # Count total leave requests
    total_leaves = db.query(func.count(LeaveApplication.LeaveApplicationId)).scalar()
    return {"total_leave_requests": total_leaves}


@router.get('/Pending-leave')
async def Pending_leave (user:user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    pending_count = db.query(func.count(LeaveApplication.LeaveApplicationId))\
                      .filter(LeaveApplication.Status == "Pending")\
                      .scalar()
    return {"pending_leave": pending_count}



@router.get('/Aproved-leave')
async def Aproved_leave (user:user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    Aproved_count = db.query(func.count(LeaveApplication.LeaveApplicationId)) \
        .filter(LeaveApplication.Status == "Approved") \
        .scalar()
    return {"Approved_leave": Aproved_count}


@router.get('/Rejected-leave')
async def Rejected_leave (user:user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    Rejected_count = db.query(func.count(LeaveApplication.LeaveApplicationId)) \
        .filter(LeaveApplication.Status == "Rejected") \
        .scalar()
    return {"Rejected_leave": Rejected_count}



@router.get('/leave-application-with-Employee-details')
async def leave_application_with_Employee_details(user:user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    # return db.query(LeaveApplication).all()
    leave_applications = db.query(LeaveApplication).options(
        joinedload(LeaveApplication.employeeid)  # This assumes you have a relationship defined
    ).all()
    return leave_applications




