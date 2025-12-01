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
from models import ActionItem, Lead, Contact, Site, Users
from .auth import get_current_user
from datetime import datetime
from schemas.schemas import ActionItemRequest


router = APIRouter(
    prefix="/ActionItem",
    tags = ['ActionItem']
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
async def read_action_item(user:user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return db.query( ActionItem).all()




@router.get('/get_single_action_item/{action_item_id}', status_code=status.HTTP_200_OK)
async def read_action_item_by_id (user:user_dependency, db:db_dependency, action_item_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    action_item_model = db.query(ActionItem).filter(ActionItem.ActionItemId == action_item_id).first()
    if action_item_model is not None:
        return action_item_model
    raise HTTPException(status_code=404, detail= 'action item not found')





# @router.post('/create_action_item', status_code=status.HTTP_201_CREATED)
# async def create_action_item(user: user_dependency, db:db_dependency, action_item_request:ActionItemRequest):
#     if user is None:
#         raise HTTPException(status_code=401, detail='Authentication Failed')
#     new_action_item = ActionItem(
#         AllotedToUserId=action_item_request.AllotedToUserId,
#         AllotedByUserId=action_item_request.AllotedByUserId,
#         CreatedDate=action_item_request.CreatedDate,
#         ProposedEndDate=action_item_request.ProposedEndDate,
#         ActualEndDate=action_item_request.ActualEndDate,
#         Description=action_item_request.Description,
#         Status = action_item_request.Status,
#         ActionItemName=action_item_request.ActionItemName,
#         LeadId=action_item_request.LeadId
#     )
#     db.add(new_action_item)
#     db.commit()
#     if new_action_item is not  None:
#         return new_action_item
#     raise HTTPException(status_code=404, detail='action item not found')



@router.post('/create_action_item', status_code=status.HTTP_201_CREATED)
async def create_action_item(user: user_dependency, db:db_dependency, action_item_request:ActionItemRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    new_action_item = ActionItem(**action_item_request.dict(), AllotedByUserId=user.get('id'), CreatedDate=get_time())
    db.add(new_action_item)
    db.commit()
    db.refresh(new_action_item)
    return {"ActionItemId": new_action_item.ActionItemId}





@router.put("/update_action_item/{action_item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_action_item(user: user_dependency, db: db_dependency, action_item_id: int, action_item_request:ActionItemRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    action_item_exist = db.query(ActionItem).filter(ActionItem.ActionItemId == action_item_id).first()
    if action_item_exist is None:
        raise HTTPException(status_code=404, detail="action item not found")
    action_item_exist.AllotedToUserId = action_item_request.AllotedToUserId
    action_item_exist.ProposedEndDate = action_item_request.ProposedEndDate
    action_item_exist.Description = action_item_request.Description
    action_item_exist.Status = action_item_request.Status
    action_item_exist.ActionItemName = action_item_request.ActionItemName
    action_item_exist.LeadId = action_item_request.LeadId
    action_item_exist.UpdateDate = get_time()
    if action_item_request.Status == "Closed":
        action_item_exist.ActualEndDate = get_time()
    db.add(action_item_exist)
    db.commit()






@router.delete("/delete_action_item/{action_item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_action_item (user: user_dependency, db: db_dependency, action_item_id : int =Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    action_item_model = db.query(ActionItem).filter(ActionItem.ActionItemId == action_item_id ).first()
    if action_item_model is None:
        raise HTTPException(status_code=404, detail="action item not found")
    db.query(ActionItem).filter(ActionItem.ActionItemId == action_item_id).delete()
    db.commit()



@router.get('/action_item_data', status_code=status.HTTP_200_OK)
async def action_item_data(user:user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    action_item_data = db.query(ActionItem).options(
              joinedload(ActionItem.lead).load_only(Lead.LeadName),
              joinedload(ActionItem.alloted_to_user_id).load_only(Users.FirstName, Users.LastName),
              joinedload(ActionItem.lead).joinedload(Lead.site).load_only(Site.SiteName),
              joinedload(ActionItem.lead).joinedload(Lead.contacts).load_only(Contact.ContactFName, Contact.ContactLName, Contact.ContactNo)
    ).all()
    return action_item_data


