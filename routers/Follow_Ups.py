from fastapi import APIRouter, Depends, HTTPException,status
from pytz import timezone
from fastapi import Path
from pydantic import BaseModel,Field
from sqlalchemy.testing.pickleable import User

from models import FollowUps, Lead, Visit, Users, Todos, ActionItem
from typing import Annotated
from sqlalchemy.orm import Session,joinedload, load_only
from sqlalchemy import  select, func
from database import SessionLocal
from .auth import get_current_user
from datetime import datetime
from schemas.schemas import FollowUpsRequest


router = APIRouter(
    prefix="/Follow_Ups",
    tags = ['Follow_Ups']
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
async def read_follow_ups(user:user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return db.query(FollowUps).all()


@router.get('/getsinglefollowups/{follow_id}', status_code=status.HTTP_200_OK)
async def read_follow_ups_by_id (user:user_dependency, db:db_dependency, follow_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    follow_model = db.query(FollowUps).filter(FollowUps.FollowUpsId == follow_id).first()
    if follow_model is not None:
        return follow_model
    raise HTTPException(status_code=404, detail= 'follow not found')


# @router.post('/createfollowups', status_code=status.HTTP_201_CREATED)
# async def create_follow_ups(user: user_dependency, db:db_dependency, followups_request:FollowUpsRequest):
#     if user is None:
#         raise HTTPException(status_code=401, detail='Authentication Failed')
#     followups = FollowUps(
#         LeadId=followups_request.LeadId,
#         VisitId=followups_request.VisitId,
#         UserId=followups_request.UserId,
#         FollowUpType=followups_request.FollowUpType,
#         Status=followups_request.Status,
#         Notes=followups_request.Notes,
#         FollowUpDate=followups_request.FollowUpDate,
#         NextFollowUpDate=followups_request.NextFollowUpDate,
#         CreatedDate=followups_request.CreatedDate,
#         UpdatedDate=followups_request.UpdatedDate,
#         CreatedById=followups_request.CreatedById
#     )
#     db.add(followups)
#     db.commit()
#     if followups_request is not None:
#         return followups_request
#     raise HTTPException(status_code=404, detail='follow ups not found')



# @router.post('/createfollowups', status_code=status.HTTP_201_CREATED)
# async def create_follow_ups(user: user_dependency, db: db_dependency, followups_request: FollowUpsRequest):
#     if user is None:
#         raise HTTPException(status_code=401, detail='Authentication Failed')
#
#     # ✅ Check if Lead exists
#     lead = db.query(Lead).filter(Lead.LeadId == followups_request.LeadId).first()
#     if not lead:
#         raise HTTPException(status_code=400, detail=f"LeadId {followups_request.LeadId} does not exist")
#
#     # visit = db.query(Visit).filter(Visit.VisitId == followups_request.VisitId).first()
#     # if not visit:
#     #     raise HTTPException(status_code=400, detail=f"VisitId {followups_request.VisitId} does not exist")
#
#     user_exists = db.query(Users).filter(Users.id == followups_request.UserId).first()
#     if not user_exists:
#         raise HTTPException(status_code=400, detail=f"UserId {followups_request.UserId} does not exist")
#
#     # ✅ Create FollowUps record
#     followups = FollowUps(
#         LeadId=followups_request.LeadId,
#         VisitId=followups_request.VisitId,
#         UserId=followups_request.UserId,
#         FollowUpType=followups_request.FollowUpType,
#         Status=followups_request.Status,
#         Notes=followups_request.Notes,
#         FollowUpDate=followups_request.FollowUpDate,
#         NextFollowUpDate=followups_request.NextFollowUpDate,
#         CreatedDate=followups_request.CreatedDate,
#         UpdatedDate=followups_request.UpdatedDate,
#         CreatedById=followups_request.CreatedById
#     )
#
#     db.add(followups)
#     db.commit()
#     db.refresh(followups)
#
#     return {"message": "Follow-up created successfully", "data": followups}

# ---------------------------------------------------------------------------------------------------------
# @router.post('/createfollowups', status_code=status.HTTP_201_CREATED)
# async def create_follow_ups(user: user_dependency, db: db_dependency, followups_request: FollowUpsRequest):
#     if user is None:
#         raise HTTPException(status_code=401, detail='Authentication Failed')
#     followups = FollowUps(** followups_request.dict(), CreatedById=user.get('id'), CreatedDate=get_time(), UpdatedDate=get_time())
#     db.add(followups)
#     db.commit()
#     db.refresh(followups)
#     # Create a todo for the assigned user
#     todo_model = Todos(
#         UserId=followups_request.UserId,  # The user assigned to the follow-up
#         Title=f"Follow-up: {followups_request.FollowUpType}",
#         Description=followups_request.Notes or "Follow-up task created",
#         Priority=1,  # Set default priority (adjust as needed)
#         Complete=False  # New todo should not be completed
#     )
#     db.add(todo_model)
#     db.commit()
#     db.refresh(todo_model)
#
#     return {
#         "FollowupsID": followups.FollowUpsId,
#         "TodoID": todo_model.TodosId  # Optional: return the created todo ID
#     }

# ---------------------------------------------------------------------------------------------------------
@router.post('/createfollowups', status_code=status.HTTP_201_CREATED)
async def create_follow_ups(user: user_dependency, db: db_dependency, followups_request: FollowUpsRequest):

    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    # Determine FollowUpType based on LeadId or VisitId
    # if followups_request.LeadId is not None:
    #     follow_up_type = "Lead Follow-up"
    # elif followups_request.VisitId is not None:
    #     follow_up_type = "Visit Follow-up"
    # else:
    #     # If neither is provided, use the type from request or default
    #     follow_up_type = followups_request.FollowUpType

    # Create follow-up record first
    followups = FollowUps(
        LeadId=followups_request.LeadId,
        VisitId=followups_request.VisitId,
        UserId=followups_request.UserId,
        FollowUpType=followups_request.FollowUpType,
        Status=followups_request.Status,
        Notes=followups_request.Notes,
        FollowUpDate=followups_request.FollowUpDate,
        NextFollowUpDate=followups_request.NextFollowUpDate,
        CreatedById=user.get('id'),
        CreatedDate=get_time(),
        UpdatedDate=get_time()
    )
    db.add(followups)
    db.commit()
    db.refresh(followups)

    # Determine ActionItemName based on LeadId or VisitId
    if followups_request.LeadId is not None:
        action_item_name = f"Lead Follow-up ({followups_request.FollowUpType})"
    elif followups_request.VisitId is not None:
        action_item_name = f"Visit Follow-up ({followups_request.FollowUpType})"
    else:
        action_item_name = followups_request.FollowUpType

    # Create ActionItem with reference to the FollowUpsId
    action_item = ActionItem(
        LeadId=followups_request.LeadId,
        VisitId=followups_request.VisitId,
        FollowUpsId=followups.FollowUpsId,
        AllotedToUserId=followups_request.UserId,
        AllotedByUserId=user.get('id'),
        ProposedEndDate=followups_request.FollowUpDate,
        Description=followups_request.Notes,
        Status='New',
        ActionItemName=action_item_name,
        CreatedDate=get_time()
    )
    db.add(action_item)
    db.commit()
    db.refresh(action_item)

    return {
        "FollowupsID": followups.FollowUpsId,
        "ActionItemId": action_item.ActionItemId
    }


@router.put("/updatefollowups/{follow_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_follow_ups(user: user_dependency, db: db_dependency, follow_id: int, followups_request:FollowUpsRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    followups_exist = db.query(FollowUps).filter(FollowUps.FollowUpsId == follow_id ).first()
    if followups_exist is None:
        raise HTTPException(status_code=404, detail="follow ups detail not found")
    followups_exist.LeadId=followups_request.LeadId
    followups_exist.VisitId=followups_request.VisitId
    followups_exist.UserId=followups_request.UserId
    followups_exist.FollowUpType=followups_request.FollowUpType
    followups_exist.Status=followups_request.Status
    followups_exist.Notes=followups_request.Notes
    followups_exist.FollowUpDate=followups_request.FollowUpDate
    followups_exist.NextFollowUpDate=followups_request.NextFollowUpDate
    # followups_exist.CreatedDate=followups_request.CreatedDate
    followups_exist.UpdatedDate= get_time()
    # followups_exist.CreatedById=followups_request.CreatedById
    db.add(followups_exist)
    db.commit()


@router.delete("/deletefollowups/{follow_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_followups (user: user_dependency, db: db_dependency, follow_id : int =Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    follow_model = db.query(FollowUps).filter(FollowUps.FollowUpsId == follow_id).first()
    if follow_model is None:
        raise HTTPException(status_code=404, detail="follow ups detail not found")
    db.query(FollowUps).filter(FollowUps.FollowUpsId == follow_id).delete()
    db.commit()



# @router.get("/follow-Ups-by-leadId/{Lead_id}",  status_code=status.HTTP_200_OK)
# async def get_followups_by_leadid(user: user_dependency, db: db_dependency, Lead_id: int = Path(gt=0)):
#     if user is None:
#         raise HTTPException(status_code=401, detail='Authentication Failed')
#
#     follow_model = db.query(FollowUps).filter(FollowUps.LeadId == Lead_id).all()
#     if not follow_model:
#         raise HTTPException(status_code=404, detail='No follow-ups found')
#     return follow_model


@router.get("/follow-Ups-by-leadId/{Lead_id}", status_code=status.HTTP_200_OK)
async def get_followups_by_leadid(user: user_dependency, db: db_dependency, Lead_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    # Query FollowUps and eagerly load only specific User fields
    follow_model = (db.query(FollowUps).options(joinedload(FollowUps.user).load_only(Users.id, Users.FirstName, Users.LastName, Users.Email, Users.ContactNo))
        .filter(FollowUps.LeadId == Lead_id)
        .all())

    if not follow_model:
        raise HTTPException(status_code=404, detail='No follow-ups found')

    # Convert to dict to include nested user info
    result = [
        {
            "FollowUpsId": f.FollowUpsId,
            "LeadId": f.LeadId,
            "VisitId": f.VisitId,
            "FollowUpType": f.FollowUpType,
            "Status": f.Status,
            "Notes": f.Notes,
            "FollowUpDate": f.FollowUpDate,
            "NextFollowUpDate": f.NextFollowUpDate,
            "User": {
                "UserId": f.user.id,
                "FirstName": f.user.FirstName,
                "LastName": f.user.LastName,
                "Email": f.user.Email,
                "ContactNo": f.user.ContactNo
            }
        }
        for f in follow_model
    ]

    return result