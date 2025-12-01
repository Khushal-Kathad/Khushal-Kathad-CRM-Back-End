from sqlalchemy import or_, and_, desc, asc, case


from fastapi import APIRouter, Depends, HTTPException,status
from pytz import timezone
from fastapi import Path
from pydantic import BaseModel,Field
from models import Lead, Contact, ProspectType, Site, InfraUnit, FollowUps, Users
from typing import Annotated, Optional
from sqlalchemy.orm import Session, joinedload, selectinload, load_only, aliased
from sqlalchemy import  select, func
from database import SessionLocal
from .auth import get_current_user
from schemas.schemas import LeadRequest
from datetime import datetime

from fastapi import Query
from routers.security_utils import get_user_site_ids

# PERFORMANCE DEBUG: Add timing and logging
import time
import logging

import redis

# Configure detailed logging for performance debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/leads",
    tags = ['leads']
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


# @router.get("/lead_search")
# async def lead_search(user:user_dependency,db: db_dependency,query: Optional[str] = Query(None),
#                          contactId: Optional[str] = Query(None), brokerId: Optional[str] = Query(None)):
#     if user is None:
#         raise HTTPException(status_code=401, detail="Authentication Failed")
#     lead_query = db.query(Lead)
#     if query:
#         lead_query = lead_query.filter(
#             or_(
#                 Lead.LeadName.ilike(f"%{query}%"),  # Search by LeadName
#                 # Lead.LeadType.ilike(f"%{query}%"),  # Search by LeadType
#                 # Lead.LeadSource.ilike(f"%{query}%"),  # Search by LeadSource
#                 # Lead.CreatedDate.ilike(f"%{query}%"),
#
#
#             )
#         )
#     if contactId:
#         # lead_query = lead_query.filter(Lead.ContactId.ilike(f"%{contactId}%"))
#         lead_query = lead_query.filter(Lead.ContactId == int(contactId))
#
#     if brokerId:
#         lead_query = lead_query.filter(Lead.BrokerId == int(brokerId))
#
#     leads = lead_query.all()
#     results = [
#         {
#             "type": "lead",
#             "data": {
#                 "LeadId": lead.LeadId,
#                 "LeadName": lead.LeadName,
#                 "ContactId": lead.ContactId,
#                 "SiteId": lead.SiteId,
#                 "InfraId": lead.InfraId,
#                 "InfraUnitId":lead.InfraUnitId,
#                 "ProspectTypeId":lead.ProspectTypeId,
#                 "CreatedById":lead.CreatedById,
#                 "LeadCreatedDate": lead.CreatedDate,
#                 "LeadClosedDate":lead.LeadClosedDate,
#                 "UpdatedDate":lead.UpdatedDate,
#                 "QuotedAmount":lead.QuotedAmount,
#                 "RequestedAmount":lead.RequestedAmount,
#                 "ClosedAmount":lead.ClosedAmount,
#                 "LeadStatus":lead.LeadStatus,
#                 "BrokerId":lead.BrokerId,
#                 "LeadType": lead.LeadType,
#                 "LeadSource": lead.LeadSource,
#                 "SuggestedUnitId": lead.SuggestedUnitId,
#                 "Bedrooms":lead.Bedrooms,
#                 "SizeSqFt":lead.SizeSqFt,
#                 "ViewType":lead.ViewType,
#                 "FloorPreference":lead.FloorPreference,
#                 "BuyingIntent":lead.BuyingIntent,
#                 "LeadPriority":lead.LeadPriority,
#                 "LeadNotes":lead.LeadNotes,
#                 "Direction":lead.Direction,
#                 "Locality":lead.Locality,
#                 "LostReasons":lead.LostReasons
#
#
#             }
#         }
#         for lead in leads
#     ]
#     # if not results:
#     # raise HTTPException(status_code=404, detail="Search not found")
#     return results
# ____________________________________________________________________________________________________________________

@router.get("/lead_search")
async def lead_search(user: user_dependency, db: db_dependency,
                      query: Optional[str] = Query(None),
                      contactId: Optional[str] = Query(None),
                      brokerId: Optional[str] = Query(None)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    allowed_site_ids = get_user_site_ids(user, db)
    if not allowed_site_ids:
        raise HTTPException(status_code=403,detail="No site access assigned for this user")

    lead_query = db.query(Lead).options(
        joinedload(Lead.contacts),
        joinedload(Lead.prospecttypes),
        joinedload(Lead.site),
        joinedload(Lead.broker),
        joinedload(Lead.created_by),
        joinedload(Lead.suggestedunit).load_only(
            InfraUnit.InfraUnitId, InfraUnit.UnitNumber)
    )

    lead_query = lead_query.filter(Lead.SiteId.in_(allowed_site_ids))

    if query:
        lead_query = lead_query.filter(
            or_(
                Lead.LeadName.ilike(f"%{query}%"),
            )
        )

    if contactId:
        lead_query = lead_query.filter(Lead.ContactId == int(contactId))

    if brokerId:
        lead_query = lead_query.filter(Lead.BrokerId == int(brokerId))

    leads = lead_query.all()
    results = []

    for lead in leads:
        results.append({
            "type": "lead",
            "data": {
                "LeadId": lead.LeadId,
                "LeadName": lead.LeadName,
                "ContactId": lead.ContactId,
                "SiteId": lead.SiteId,
                "InfraId": lead.InfraId,
                "InfraUnitId": lead.InfraUnitId,
                "ProspectTypeId": lead.ProspectTypeId,
                "CreatedById": lead.CreatedById,
                "LeadCreatedDate": lead.CreatedDate,
                "LeadClosedDate": lead.LeadClosedDate,
                "UpdatedDate": lead.UpdatedDate,
                "QuotedAmount": lead.QuotedAmount,
                "RequestedAmount": lead.RequestedAmount,
                "ClosedAmount": lead.ClosedAmount,
                "LeadStatus": lead.LeadStatus,
                "BrokerId": lead.BrokerId,
                "LeadType": lead.LeadType,
                "LeadSource": lead.LeadSource,
                "SuggestedUnitId": lead.SuggestedUnitId,
                "Bedrooms": lead.Bedrooms,
                "SizeSqFt": lead.SizeSqFt,
                "ViewType": lead.ViewType,
                "FloorPreference": lead.FloorPreference,
                "BuyingIntent": lead.BuyingIntent,
                "LeadPriority": lead.LeadPriority,
                "LeadNotes": lead.LeadNotes,
                "Direction": lead.Direction,
                "Locality": lead.Locality,
                "LostReasons": lead.LostReasons,

                # Full contact details
                "contacts": vars(lead.contacts) if lead.contacts else None,

                # Full nested object data
                "created_by": vars(lead.created_by) if lead.created_by else None,
                "broker": vars(lead.broker) if lead.broker else None,
                "prospecttypes": vars(lead.prospecttypes) if lead.prospecttypes else None,
                "site": vars(lead.site) if lead.site else None,

                # Suggested unit (partial)
                "SuggestedUnit": {
                    "InfraUnitId": lead.suggestedunit.InfraUnitId,
                    "UnitNumber": lead.suggestedunit.UnitNumber
                } if lead.suggestedunit else None
            }
        })

    return results


@router.get("/")
async def read_all_leads (user:user_dependency, db: db_dependency):
    # PERFORMANCE DEBUG: Start timing
    start_time = time.time()
    logger.info("="*80)
    logger.info("GET /leads/ - Starting request")

    if user is None:
        raise HTTPException (status_code=401, detail='Authentication Failed')

    auth_time = time.time()
    logger.info(f"Authentication check: {(auth_time - start_time)*1000:.2f}ms")

    allowed_site_ids = get_user_site_ids(user, db)
    if not allowed_site_ids:
        raise HTTPException(status_code=403, detail="No site access assigned for this user")

    site_check_time = time.time()
    logger.info(f"Site access check: {(site_check_time - auth_time)*1000:.2f}ms")
    logger.info(f"User has access to {len(allowed_site_ids)} sites")

    # Execute main query (without eager loading for now - needs indexes first)
    query_start = time.time()
    leads = db.query(Lead).filter(Lead.SiteId.in_(allowed_site_ids)).all()
    query_end = time.time()

    logger.info(f"Main query execution: {(query_end - query_start)*1000:.2f}ms")
    logger.info(f"Number of leads returned: {len(leads)}")

    # Total time
    total_time = time.time() - start_time
    logger.info(f"TOTAL REQUEST TIME: {total_time*1000:.2f}ms ({total_time:.2f}s)")
    logger.info("="*80)

    return leads



@router.get("/getsinglelead/{lead_id}", status_code=status.HTTP_200_OK )
async def read_leads_by_id (user:user_dependency, db: db_dependency,lead_id :int=Path(gt=0)):
    if user is None:
        raise HTTPException (status_code=401, detail='Authentication Failed')
    lead_model = db.query(Lead).filter(Lead.LeadId==lead_id).first()
        # .filter(Lead.CreatedById==user.get('id')).first()
    if lead_model is None:
        raise HTTPException(status_code=404, detail = 'Lead not found')
    return lead_model



# @router.post("/CreateLead", status_code=status.HTTP_201_CREATED )
# async def create_leads (user: user_dependency, db: db_dependency,
#                        lead_request:LeadRequest):
#      if user is None:
#          raise HTTPException (status_code=401, detail='Authentication Failed')
#      todo_model = Lead(**lead_request.dict(),CreatedById = user.get('id'),CreatedDate = get_time(),UpdatedDate=get_time())
#      db.add(todo_model)
#      db.commit()



@router.post("/CreateLead", status_code=status.HTTP_201_CREATED)
async def create_leads(user: user_dependency, db: db_dependency, lead_request: LeadRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    todo_model = Lead(**lead_request.dict(), CreatedById=user.get('id'), CreatedDate=get_time(), UpdatedDate=get_time())
    db.add(todo_model)
    db.commit()
    db.refresh(todo_model)  # This ensures we get the generated ID
    # Return the created lead with LeadId
    return {"LeadId": todo_model.LeadId}


@router.put("/LeadUpdate/{leadid}",status_code=status.HTTP_204_NO_CONTENT )
async def update_leads (user: user_dependency,db: db_dependency,leadid: int ,lead_request:LeadRequest):
    if user is None:
        raise HTTPException (status_code=401, detail='Authentication Failed')
    allowed_site_ids = get_user_site_ids(user, db)
    if not allowed_site_ids:
        raise HTTPException(status_code=403, detail="No site access assigned for this user")
    lead_model = db.query(Lead).filter(Lead.LeadId==leadid, Lead.SiteId.in_(allowed_site_ids)).first()
    if lead_model is None:
        raise HTTPException (status_code=404, detail="Lead not found")
    lead_model.LeadName = lead_request.LeadName
    lead_model.ContactId = lead_request.ContactId
    lead_model.SiteId = lead_request.SiteId
    lead_model.InfraId = lead_request.InfraId
    lead_model.InfraUnitId = lead_request.InfraUnitId
    lead_model.ProspectTypeId = lead_request.ProspectTypeId
    lead_model.QuotedAmount = lead_request.QuotedAmount
    lead_model.RequestedAmount= lead_request.RequestedAmount
    lead_model.ClosedAmount = lead_request.ClosedAmount
    lead_model.LeadStatus = lead_request.LeadStatus
    lead_model.BrokerId = lead_request.BrokerId
    lead_model.SuggestedUnitId = lead_request.SuggestedUnitId
    lead_model.Bedrooms = lead_request.Bedrooms
    lead_model.SizeSqFt = lead_request.SizeSqFt
    lead_model.ViewType = lead_request.ViewType
    lead_model.FloorPreference = lead_request.FloorPreference
    lead_model.BuyingIntent = lead_request.BuyingIntent
    lead_model.LeadPriority = lead_request.LeadPriority
    lead_model.LeadType = lead_request.LeadType
    lead_model.LeadSource = lead_request.LeadSource
    lead_model.LeadNotes = lead_request.LeadNotes
    lead_model.Direction = lead_request.Direction
    lead_model.Locality = lead_request.Locality
    lead_model.LostReasons = lead_request.LostReasons
    lead_model.UpdatedDate = get_time()
    db.add(lead_model)
    db.commit()


@router.patch("/LeadUpdate/{leadid}", status_code=status.HTTP_204_NO_CONTENT)
async def update_leads(user: user_dependency,db: db_dependency,leadid: int,lead_request: LeadRequest):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    allowed_site_ids = get_user_site_ids(user, db)
    if not allowed_site_ids:
        raise HTTPException(status_code=403, detail="No site access assigned for this user")
    lead_model = db.query(Lead).filter(Lead.LeadId == leadid, Lead.SiteId.in_(allowed_site_ids)).first()
    if lead_model is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    update_data = lead_request.dict(exclude_unset=True)
    lead_status = update_data.get("LeadStatus")
    if lead_status in ["Win", "Lost"]:
        update_data["LeadClosedDate"] = get_time()
    for field, value in update_data.items():
        setattr(lead_model, field, value)
    lead_model.UpdatedDate = get_time()
    db.add(lead_model)
    db.commit()





@router.delete("/LeadDelete/{leadid}", status_code=status.HTTP_204_NO_CONTENT )
async def delete_leads (user:user_dependency, db: db_dependency,leadid: int =Path(gt=0)):
    if user is None:
        raise HTTPException (status_code=401, detail='Authentication Failed')
    lead_model = db.query(Lead).filter(Lead.LeadId==leadid).filter(Lead.CreatedById == user.get('id')).first()
    if lead_model is None:
        raise HTTPException (status_code=404, detail="Lead not found")
    db.query(Lead).filter(Lead.LeadId==leadid).delete()
    db.commit()


@router.patch("/SoftDeleteLead/{leadid}", status_code=status.HTTP_200_OK)
async def soft_delete_lead(user: user_dependency, db: db_dependency, leadid: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    allowed_site_ids = get_user_site_ids(user, db)
    if not allowed_site_ids:
        raise HTTPException(status_code=403, detail="No site access assigned for this user")

    lead_model = db.query(Lead).filter(Lead.LeadId == leadid, Lead.SiteId.in_(allowed_site_ids)).first()
    if lead_model is None:
        raise HTTPException(status_code=404, detail="Lead not found")

    if lead_model.IsDeleted == 1:
        raise HTTPException(status_code=400, detail="Lead is already deleted")

    lead_model.IsDeleted = 1
    lead_model.UpdatedDate = get_time()
    db.commit()

    return {
        "message": "Lead soft deleted successfully",
        "LeadId": leadid,
        "statusCode": 200
    }


# @router.get("/buyerwiseleads", status_code=status.HTTP_200_OK )
# async def read_buyerwise_leads (user:user_dependency, db: db_dependency):
#     if user is None:
#         raise HTTPException (status_code=401, detail='Authentication Failed')
#     buyerwiseleads = db.query(Lead).options(joinedload(Lead.contacts).load_only(Contact.ContactFName,
#                      Contact.ContactLName,Contact.ContactEmail,Contact.ContactNo),\
#                      joinedload(Lead.prospecttypes).load_only(ProspectType.ProspectTypeName),
#                      joinedload(Lead.site).load_only(Site.SiteName)
#     ).all()
#     return buyerwiseleads


@router.get("/buyerwiseleads", status_code=status.HTTP_200_OK)
async def read_buyerwise_leads(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    allowed_site_ids = get_user_site_ids(user, db)
    if not allowed_site_ids:
        raise HTTPException(status_code=403,detail="No site access assigned for this user")
    # Query leads restricted by site permissions
    buyerwiseleads = (
        db.query(Lead)
        .options(
            joinedload(Lead.contacts).load_only(
                Contact.ContactFName,
                Contact.ContactLName,
                Contact.ContactEmail,
                Contact.ContactNo,
            ),
            joinedload(Lead.prospecttypes).load_only(ProspectType.ProspectTypeName),
            joinedload(Lead.site).load_only(Site.SiteName),
        )
        .filter(Lead.SiteId.in_(allowed_site_ids))
        .all()
    )
    return buyerwiseleads




@router.get("/paginationbuyerwiseleads", status_code=status.HTTP_200_OK )
async def read_paginationbuyerwise_leads (user:user_dependency, db: db_dependency, sIndex: int = Query(1, alias="sIndex"),  # Start index (1-based like Zoho)
    limit: int = Query(20)):
    if user is None:
        raise HTTPException (status_code=401, detail='Authentication Failed')
    allowed_site_ids = get_user_site_ids(user, db)
    if not allowed_site_ids:
        raise HTTPException(status_code=403, detail="No site access assigned for this user")
    offset = max(sIndex - 1, 0)
    query = (db.query(Lead).options(joinedload(Lead.contacts).load_only(Contact.ContactFName,
                     Contact.ContactLName,Contact.ContactEmail,Contact.ContactNo),\
                     joinedload(Lead.prospecttypes).load_only(ProspectType.ProspectTypeName),
                     joinedload(Lead.site).load_only(Site.SiteName)
                                    )
             .filter(Lead.SiteId.in_(allowed_site_ids))
             .order_by(Lead.LeadId.asc())  # ✅ Important for MSSQL OFFSET
             )

    buyerwiseleads = query.offset(offset).limit(limit).all()

    total_records = (
        db.query(func.count(Lead.LeadId))
        .filter(Lead.SiteId.in_(allowed_site_ids))
        .scalar()
    )

    next_index = sIndex + limit
    if next_index > total_records:
        next_index = 1

    return {
        "data": buyerwiseleads,
        "total_records": total_records,
        "sIndex": sIndex,
        "limit": limit,
        "nextIndex": next_index
    }

@router.get("/count/{statustext}")
async def get_lead_count(user:user_dependency, db: db_dependency,statustext: str):
    if user is None:
        raise HTTPException (status_code=401, detail='Authentication Failed')
    lead_count = db.query(Lead).filter(Lead.LeadStatus==statustext).count()
    return {"lead_count": lead_count}


# @router.get("/sitewisecount/")
# async def get_lead_count_by_site(user:user_dependency, db: db_dependency):
#     if user is None:
#         raise HTTPException (status_code=401, detail='Authentication Failed')
#     query = (
#         db.query(Site.SiteName, func.count(Lead.LeadId).label("lead_count"))
#         .join(Lead, Site.SiteId == Lead.SiteId)
#         .group_by(Site.SiteName, Lead.LeadStatus))
#     result = query.all()
#     counts = {row[0]: row[1] for row in result}
#     return counts


@router.get("/sitewisecount/")
async def get_lead_count_by_site(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    query = (
        db.query(
            Site.SiteName, Lead.LeadStatus, func.count(Lead.LeadId).label("lead_count")
        )
        .join(Lead, Site.SiteId == Lead.SiteId)
        .group_by(Site.SiteName, Lead.LeadStatus)
    )
    result = query.all()
    print(result)
    output = {}
    for row in result:
        site_name = row[0]
        lead_status = row[1]
        lead_count = row[2]
        if site_name not in output:
            output[site_name] = {}
        output[site_name][lead_status] = lead_count
    return output




@router.get("/getleaddetails/{lead_id}", status_code=status.HTTP_200_OK)
async def read_leads_details(user: user_dependency,db: db_dependency,lead_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    lead_model = db.query(Lead).options(
        joinedload(Lead.contacts),
        joinedload(Lead.prospecttypes),
        joinedload(Lead.site),
        joinedload(Lead.broker),
        joinedload(Lead.created_by),
        joinedload(Lead.suggestedunit)
    ).filter(
        Lead.LeadId == lead_id
        # Lead.CreatedById == user.get('id')
    ).first()
    if lead_model is not None:
        return lead_model
    raise HTTPException(status_code=404, detail='Lead not found')





# @router.get("/leads_full_detail", status_code=status.HTTP_200_OK )
# async def read_leads_full_details (user:user_dependency, db: db_dependency):
#     if user is None:
#         raise HTTPException (status_code=401, detail='Authentication Failed')
#     lead_details = db.query(Lead).options(joinedload(Lead.contacts).load_only(Contact.ContactId, Contact.ContactFName,
#                      Contact.ContactLName, Contact.ContactEmail, Contact.ContactNo, Contact.ContactCity, Contact.ContactState,
#                      Contact.ContactAddress, Contact.ContactPostalCode, Contact.ContactType, Contact.CreatedDate, Contact.UpdatedDate,
#                      Contact.CreatedById),
#                      joinedload(Lead.prospecttypes),
#                      joinedload(Lead.site),
#                      joinedload(Lead.broker),
#                      joinedload(Lead.created_by),
#                      joinedload(Lead.suggestedunit).load_only(InfraUnit.InfraUnitId, InfraUnit.UnitNumber)
#     ).all()
#     return lead_details







# Connect to Redis (Make sure Redis is running)
# redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
# @router.get("/leads_full_detail", status_code=status.HTTP_200_OK)
# async def read_leads_full_details (user:user_dependency, db: db_dependency):
#     if user is None:
#         raise HTTPException(status_code=401, detail='Authentication Failed')
#     last_offset = 0 if redis_client is None else redis_client.get("lead_offset") or 0
#     last_offset = int(last_offset)
#     lead_details = db.query(Lead).options(
#         joinedload(Lead.contacts).load_only(
#             Contact.ContactId, Contact.ContactFName, Contact.ContactLName, Contact.ContactEmail,
#             Contact.ContactNo, Contact.ContactCity, Contact.ContactState, Contact.ContactAddress,
#             Contact.ContactPostalCode, Contact.ContactType, Contact.CreatedDate, Contact.UpdatedDate,
#             Contact.CreatedById),
#         joinedload(Lead.prospecttypes),
#         joinedload(Lead.site),
#         joinedload(Lead.broker),
#         joinedload(Lead.created_by),
#         joinedload(Lead.suggestedunit).load_only(
#             InfraUnit.InfraUnitId, InfraUnit.UnitNumber)
#     ).order_by(Lead.LeadId).offset(last_offset).limit(20).all()
#     total_records = db.query(Lead).count()
#     next_offset = last_offset + 20
#     if next_offset >= total_records:  # Reset if end reached
#         next_offset = 0
#     if redis_client:
#         redis_client.set("lead_offset", next_offset)  # Save next offset in Redis
#     return {
#         "data": lead_details,
#         "total_records": total_records,
#         "current_offset": last_offset,
#         "next_offset": next_offset
#     }



# @router.get("/leads_full_detail", status_code=status.HTTP_200_OK)
# async def read_leads_full_details(
#     user: user_dependency,
#     db: db_dependency,
#     sIndex: int = Query(1, alias="sIndex"),  # Start index (1-based like Zoho)
#     limit: int = Query(20)
# ):
#     if user is None:
#         raise HTTPException(status_code=401, detail='Authentication Failed')
#
#     # Convert 1-based index to 0-based offset
#     offset = max(sIndex - 1, 0)
#     print(offset)
#
#     lead_details = db.query(Lead).options(
#         joinedload(Lead.contacts).load_only(
#             Contact.ContactId, Contact.ContactFName, Contact.ContactLName, Contact.ContactEmail,
#             Contact.ContactNo, Contact.ContactCity, Contact.ContactState, Contact.ContactAddress,
#             Contact.ContactPostalCode, Contact.ContactType, Contact.CreatedDate, Contact.UpdatedDate,
#             Contact.CreatedById),
#         joinedload(Lead.prospecttypes),
#         joinedload(Lead.site),
#         joinedload(Lead.broker),
#         joinedload(Lead.created_by),
#         joinedload(Lead.suggestedunit).load_only(
#             InfraUnit.InfraUnitId, InfraUnit.UnitNumber)
#     ).order_by(Lead.LeadId).offset(offset).limit(limit).all()
#
#     total_records = db.query(Lead).count()
#     next_index = sIndex + limit
#     if next_index > total_records:
#         next_index = 1  # Reset to start
#
#     return {
#         "data": lead_details,
#         "total_records": total_records,
#         "sIndex": sIndex,
#         "limit": limit,
#         "nextIndex": next_index
#     }






# @router.get("/leads_full_detail", status_code=status.HTTP_200_OK)
# async def read_leads_full_details(user: user_dependency,db: db_dependency,sIndex: int = Query(1, alias="sIndex"),limit: int = Query(20),
#     LeadStatus: list [str] | None = Query(None),
#     LeadSource: list [str] | None = Query(None),
#     SiteName: list [str] | None = Query(None),
#     ProspectTypeName: list [str] | None = Query(None),
#
#     BrokerName: str | None = Query(None),
#     BrokerNumber: str | None = Query(None),
#     CustomerName: str | None = Query(None),
#     CustomerNo: str | None = Query(None)
# ):
#     if user is None:
#         raise HTTPException(status_code=401, detail='Authentication Failed')
#     allowed_site_ids = get_user_site_ids(user, db)
#     if not allowed_site_ids:
#         raise HTTPException(status_code=403,detail="No site access assigned for this user")
#
#     offset = max(sIndex - 1, 0)
#
#     query = db.query(Lead).options(
#         joinedload(Lead.contacts).load_only(
#             Contact.ContactId, Contact.ContactFName, Contact.ContactLName,
#             Contact.ContactEmail, Contact.ContactNo, Contact.ContactCity,
#             Contact.ContactState, Contact.ContactAddress, Contact.ContactPostalCode,
#             Contact.ContactType, Contact.CreatedDate, Contact.UpdatedDate,
#             Contact.CreatedById
#         ),
#         joinedload(Lead.prospecttypes),
#         joinedload(Lead.site),
#         joinedload(Lead.broker),
#         joinedload(Lead.created_by),
#         joinedload(Lead.suggestedunit).load_only(
#             InfraUnit.InfraUnitId, InfraUnit.UnitNumber
#         )
#     )
#
#     # Filter by allowed sites first
#     query = query.filter(Lead.SiteId.in_(allowed_site_ids))
#
#     # Track if any filter was applied
#     filter_applied = False
#
#     if LeadStatus:
#         filter_applied = True
#         query = query.filter(Lead.LeadStatus.in_(LeadStatus))
#
#     if LeadSource:
#         filter_applied = True
#         query = query.filter(Lead.LeadSource.in_(LeadSource))
#
#     if SiteName:
#         filter_applied = True
#         query = query.join(Lead.site).filter(Site.SiteName.in_(SiteName))
#
#     if ProspectTypeName:
#         filter_applied = True
#         query = query.join(Lead.prospecttypes).filter(ProspectType.ProspectTypeName.in_(ProspectTypeName))
#
#     if BrokerName:
#         filter_applied = True
#         query = query.join(Lead.broker).filter(
#             or_(
#                 func.concat(Contact.ContactFName, ' ', Contact.ContactLName).ilike(f"%{BrokerName}%"),
#                 Contact.ContactFName.ilike(f"%{BrokerName}%"),
#                 Contact.ContactLName.ilike(f"%{BrokerName}%")
#             )
#         )
#     if BrokerNumber:   # ✅ New filter for Broker ContactNo
#         filter_applied = True
#         query = query.join(Lead.broker).filter(
#             and_(
#                 Contact.ContactType == 'Broker',
#                 Contact.ContactNo.ilike(f"%{BrokerNumber}%")
#             )
#         )
#     if CustomerName:
#         filter_applied = True
#         query = query.join(Lead.contacts).filter(
#             and_(
#                 Contact.ContactType == 'Customer',
#                 or_(
#                     func.concat(Contact.ContactFName, ' ', Contact.ContactLName).ilike(f"%{CustomerName}%"),
#                     Contact.ContactFName.ilike(f"%{CustomerName}%"),
#                     Contact.ContactLName.ilike(f"%{CustomerName}%"),
#
#                 )
#             )
#         )
#     if CustomerNo:
#         filter_applied = True
#         query = query.join(Lead.contacts).filter(
#             and_(
#                 Contact.ContactType == 'Customer',
#                 Contact.ContactNo.ilike(f"%{CustomerNo}%")
#             )
#         )
#
#     total_records = query.count()
#
#
#     if filter_applied and total_records == 0:
#         raise HTTPException(
#             status_code=404,
#             detail="No records found for the given filter(s)."
#         )
#
#     lead_details = query.order_by(Lead.LeadId).offset(offset).limit(limit).all()
#
#     next_index = sIndex + limit
#     if next_index > total_records:
#         next_index = 1  # Reset to start
#
#     return {
#         "data": lead_details,
#         "total_records": total_records,
#         "sIndex": sIndex,
#         "limit": limit,
#         "nextIndex": next_index
#     }

# ----------------------------------------------------------------------------------------------------------


@router.get("/leads_full_detail", status_code=status.HTTP_200_OK)
async def read_leads_full_details(
    user: user_dependency,
    db: db_dependency,
    sIndex: int = Query(1, alias="sIndex"),
    limit: int = Query(20),
    LeadStatus: Optional[list[str]] = Query(None),
    LeadSource: Optional[list[str]] = Query(None),
    SiteName: Optional[list[str]] = Query(None),
    ProspectTypeName: Optional[list[str]] = Query(None),
    BrokerName: Optional[list[str]] = Query(None),
    BrokerNumber: Optional[list[str]] = Query(None),
    CustomerName: Optional[list[str]] = Query(None),
    CustomerNo: Optional[list[str]] = Query(None),
    StartDate: Optional[str] = Query(None),
    EndDate: Optional[str] = Query(None),
    # NEW: Intelligence filters with dynamic ranges
    HealthScoreMin: Optional[int] = Query(None),  # Minimum health score (0-100)
    HealthScoreMax: Optional[int] = Query(None),  # Maximum health score (0-100)
    ChurnRisk: Optional[list[str]] = Query(None),   # low, medium, high, critical
    FollowUpStatus: Optional[list[str]] = Query(None),  # overdue, today, this_week, scheduled, none
    BuyingIntentMin: Optional[int] = Query(None),  # Minimum buying intent (0-10)
    BuyingIntentMax: Optional[int] = Query(None),  # Maximum buying intent (0-10)
    OverdueDaysMin: Optional[int] = Query(None),  # Minimum overdue days
    OverdueDaysMax: Optional[int] = Query(None),  # Maximum overdue days
    sortBy: Optional[str] = Query("created_date_desc"),  # ai_priority, health_score_asc, health_score_desc, buying_intent_desc, created_date_desc, created_date_asc, lead_name_asc, budget_desc, follow_up_date, last_contact_date
):

    # PERFORMANCE DEBUG: Start comprehensive timing
    start_time = time.time()
    logger.info("="*80)
    logger.info("GET /leads/leads_full_detail - Starting request")
    logger.info(f"Parameters: sIndex={sIndex}, limit={limit}, sortBy={sortBy}")
    logger.info(f"Filters: LeadStatus={LeadStatus}, LeadSource={LeadSource}, SiteName={SiteName}")

    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    auth_time = time.time()
    logger.info(f"[1] Authentication: {(auth_time - start_time)*1000:.2f}ms")

    allowed_site_ids = get_user_site_ids(user, db)
    if not allowed_site_ids:
        raise HTTPException(status_code=403, detail="No site access assigned for this user")

    site_check_time = time.time()
    logger.info(f"[2] Site access check: {(site_check_time - auth_time)*1000:.2f}ms - {len(allowed_site_ids)} sites")

    offset = max(sIndex - 1, 0)

    # Create aliases for contact table to avoid conflicts when joining multiple times
    BrokerContact = aliased(Contact)
    CustomerContact = aliased(Contact)

    # PERFORMANCE FIX: Use selectinload instead of joinedload
    # selectinload uses separate queries (N+1 style) which is MUCH faster than
    # massive JOINs with cartesian products when dealing with multiple relationships
    query = db.query(Lead).options(
        selectinload(Lead.contacts).load_only(
            Contact.ContactId, Contact.ContactFName, Contact.ContactLName,
            Contact.ContactEmail, Contact.ContactNo,
            Contact.ContactType
        ),
        selectinload(Lead.prospecttypes),
        selectinload(Lead.site),
        selectinload(Lead.broker),
        selectinload(Lead.created_by),
        selectinload(Lead.suggestedunit).load_only(
            InfraUnit.InfraUnitId, InfraUnit.UnitNumber
        )
    )

    # Filter by allowed sites first
    query = query.filter(Lead.SiteId.in_(allowed_site_ids))

    # Track if any filter was applied
    filter_applied = False

    if LeadStatus:
        filter_applied = True
        query = query.filter(Lead.LeadStatus.in_(LeadStatus))
    if LeadSource:
        filter_applied = True
        query = query.filter(Lead.LeadSource.in_(LeadSource))
    if SiteName:
        filter_applied = True
        query = query.join(Lead.site).filter(
            or_(*[Site.SiteName.ilike(f"%{name}%") for name in SiteName])
        )
    if ProspectTypeName:
        filter_applied = True
        query = query.join(Lead.prospecttypes).filter(
            or_(*[ProspectType.ProspectTypeName.ilike(f"%{name}%") for name in ProspectTypeName])
        )
    if BrokerName:
        filter_applied = True
        query = query.join(BrokerContact, Lead.broker)
        # Build a list of OR conditions for each name in the list
        name_conditions = []
        for name in BrokerName:
            # Strip whitespace from the search term
            name = name.strip()
            if not name:  # Skip empty strings
                continue
            # Check if it matches first name, last name, or full name (first + last)
            name_conditions.append(
                or_(
                    BrokerContact.ContactFName.ilike(f"%{name}%"),
                    BrokerContact.ContactLName.ilike(f"%{name}%"),
                    (BrokerContact.ContactFName + ' ' + BrokerContact.ContactLName).ilike(f"%{name}%")
                )
            )
        if name_conditions:  # Only filter if we have valid conditions
            query = query.filter(or_(*name_conditions))
    if BrokerNumber:
        filter_applied = True
        query = query.join(BrokerContact, Lead.broker).filter(
            and_(
                BrokerContact.ContactType == 'Broker',
                or_(*[BrokerContact.ContactNo.ilike(f"%{num}%") for num in BrokerNumber])
            )
        )
    if CustomerName:
        filter_applied = True
        query = query.join(CustomerContact, Lead.contacts)
        # Build a list of OR conditions for each name in the list
        name_conditions = []
        for name in CustomerName:
            # Strip whitespace from the search term
            name = name.strip()
            if not name:  # Skip empty strings
                continue
            # Check if it matches first name, last name, or full name (first + last)
            name_conditions.append(
                or_(
                    CustomerContact.ContactFName.ilike(f"%{name}%"),
                    CustomerContact.ContactLName.ilike(f"%{name}%"),
                    (CustomerContact.ContactFName + ' ' + CustomerContact.ContactLName).ilike(f"%{name}%")
                )
            )
        if name_conditions:  # Only filter if we have valid conditions
            query = query.filter(
                and_(
                    CustomerContact.ContactType == 'Customer',
                    or_(*name_conditions)
                )
            )
    if CustomerNo:
        filter_applied = True
        query = query.join(CustomerContact, Lead.contacts).filter(
            and_(
                CustomerContact.ContactType == 'Customer',
                or_(*[CustomerContact.ContactNo.ilike(f"%{num}%") for num in CustomerNo])
            )
        )

    if StartDate and EndDate:
        filter_applied = True
        try:
            start_date = datetime.strptime(StartDate, "%Y-%m-%d")
            end_date = datetime.strptime(EndDate, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
            query = query.filter(
                and_(
                    Lead.CreatedDate >= start_date,
                    Lead.CreatedDate <= end_date
                )
            )
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")
    elif StartDate:
        filter_applied = True
        try:
            start_date = datetime.strptime(StartDate, "%Y-%m-%d")
            query = query.filter(Lead.CreatedDate >= start_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")
    elif EndDate:
        filter_applied = True
        try:
            end_date = datetime.strptime(EndDate, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
            query = query.filter(Lead.CreatedDate <= end_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    # NEW: Intelligence filters with dynamic min-max ranges
    if HealthScoreMin is not None or HealthScoreMax is not None:
        filter_applied = True
        if HealthScoreMin is not None and HealthScoreMax is not None:
            # Both min and max provided
            query = query.filter(and_(
                Lead.HealthScore >= HealthScoreMin,
                Lead.HealthScore <= HealthScoreMax
            ))
        elif HealthScoreMin is not None:
            # Only min provided
            query = query.filter(Lead.HealthScore >= HealthScoreMin)
        elif HealthScoreMax is not None:
            # Only max provided
            query = query.filter(Lead.HealthScore <= HealthScoreMax)

    if ChurnRisk:
        filter_applied = True
        query = query.filter(Lead.ChurnRisk.in_(ChurnRisk))

    if FollowUpStatus:
        filter_applied = True
        query = query.filter(Lead.FollowUpStatus.in_(FollowUpStatus))

    if BuyingIntentMin is not None or BuyingIntentMax is not None:
        filter_applied = True
        if BuyingIntentMin is not None and BuyingIntentMax is not None:
            # Both min and max provided
            query = query.filter(and_(
                Lead.BuyingIntent >= BuyingIntentMin,
                Lead.BuyingIntent <= BuyingIntentMax
            ))
        elif BuyingIntentMin is not None:
            # Only min provided
            query = query.filter(Lead.BuyingIntent >= BuyingIntentMin)
        elif BuyingIntentMax is not None:
            # Only max provided
            query = query.filter(Lead.BuyingIntent <= BuyingIntentMax)

    if OverdueDaysMin is not None or OverdueDaysMax is not None:
        filter_applied = True
        if OverdueDaysMin is not None and OverdueDaysMax is not None:
            # Both min and max provided
            query = query.filter(and_(
                Lead.OverdueDays >= OverdueDaysMin,
                Lead.OverdueDays <= OverdueDaysMax
            ))
        elif OverdueDaysMin is not None:
            # Only min provided
            query = query.filter(Lead.OverdueDays >= OverdueDaysMin)
        elif OverdueDaysMax is not None:
            # Only max provided
            query = query.filter(Lead.OverdueDays <= OverdueDaysMax)

    query_build_time = time.time()
    logger.info(f"[3] Query building (with filters): {(query_build_time - site_check_time)*1000:.2f}ms")

    # BUG FIX: Use query.count() to include ALL filters AND JOINs
    # Previous approach only copied WHERE conditions but missed JOINs entirely,
    # causing wrong counts when filtering by Customer/Broker/Site/ProspectType
    count_start = time.time()
    total_records = query.count()
    count_end = time.time()
    logger.info(f"[4] COUNT query execution: {(count_end - count_start)*1000:.2f}ms - {total_records} total records")


    if filter_applied and total_records == 0:
        raise HTTPException(
            status_code=404,
            detail="No records found for the given filter(s)."
        )

    # PERFORMANCE OPTIMIZATION: Dictionary-based sorting (O(1) lookup vs O(n) if-elif chain)
    # Cleaner, faster, and more maintainable than long if-elif chains
    from sqlalchemy import func as sqlfunc

    # Dictionary mapping for simple sort configurations (no query modifications needed)
    # PERFORMANCE: Direct column sorting - SQL Server handles NULLs automatically
    # NULLs are sorted first by default in SQL Server (which is fine for our use case)
    SORT_CONFIGURATIONS = {
        "ai_priority": lambda: [desc(Lead.AIPriority)],
        "health_score_asc": lambda: [asc(Lead.HealthScore)],
        "health_score_desc": lambda: [desc(Lead.HealthScore)],
        "buying_intent_desc": lambda: [desc(Lead.BuyingIntent)],
        "created_date_desc": lambda: [desc(Lead.CreatedDate)],
        "created_date_asc": lambda: [asc(Lead.CreatedDate)],
        "lead_name_asc": lambda: [asc(Lead.LeadName)],
        "budget_desc": lambda: [desc(sqlfunc.coalesce(Lead.RequestedAmount, Lead.QuotedAmount, 0))],
    }

    # Handle complex sorts that require query modifications (subqueries/joins)
    if sortBy == "follow_up_date":
        # Follow-up Date - earliest first, NULLs last
        next_followup_subquery = (
            db.query(
                FollowUps.LeadId,
                func.min(FollowUps.NextFollowUpDate).label('next_followup')
            )
            .filter(FollowUps.Status != 'Completed')
            .group_by(FollowUps.LeadId)
            .subquery()
        )
        query = query.outerjoin(
            next_followup_subquery,
            Lead.LeadId == next_followup_subquery.c.LeadId
        )
        sort_orders = [asc(next_followup_subquery.c.next_followup)]
    elif sortBy == "last_contact_date":
        # Last Contact Date - most recent first (DESC)
        last_followup_subquery = (
            db.query(
                FollowUps.LeadId,
                func.max(FollowUps.FollowUpDate).label('last_contact')
            )
            .filter(FollowUps.Status == 'Completed')
            .group_by(FollowUps.LeadId)
            .subquery()
        )
        query = query.outerjoin(
            last_followup_subquery,
            Lead.LeadId == last_followup_subquery.c.LeadId
        )
        sort_orders = [desc(last_followup_subquery.c.last_contact)]
    else:
        # Use dictionary lookup for all other sorts (O(1) constant time lookup!)
        # Default to ai_priority if sortBy is not found in dictionary
        sort_func = SORT_CONFIGURATIONS.get(sortBy, SORT_CONFIGURATIONS["ai_priority"])
        sort_orders = sort_func()

    # Apply sorting with NULL handling for SQL Server
    # PERFORMANCE DEBUG: Measure main query with sorting and pagination
    main_query_start = time.time()
    lead_details = query.order_by(*sort_orders).offset(offset).limit(limit).all()
    main_query_end = time.time()
    logger.info(f"[5] Main query execution (sort + pagination): {(main_query_end - main_query_start)*1000:.2f}ms - {len(lead_details)} leads returned")

    next_index = sIndex + limit
    if next_index > total_records:
        next_index = 1  # Reset to start

    # PERFORMANCE DEBUG: Total request time
    total_time = time.time() - start_time
    logger.info(f"TOTAL REQUEST TIME: {total_time*1000:.2f}ms ({total_time:.2f}s)")
    logger.info("="*80)

    return {
        "data": lead_details,
        "total_records": total_records,
        "sIndex": sIndex,
        "limit": limit,
        "nextIndex": next_index
    }


@router.get("/leads_aggregates", status_code=status.HTTP_200_OK)
async def get_leads_aggregates(
    user: user_dependency,
    db: db_dependency,
):
    """
    Get aggregate counts for all leads (no filtering applied).
    Returns summary statistics for all leads the user has access to based on site permissions.
    """
    start_time = time.time()
    logger.info("="*80)
    logger.info("GET /leads/leads_aggregates - Starting request")

    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    auth_time = time.time()
    logger.info(f"[1] Authentication: {(auth_time - start_time)*1000:.2f}ms")

    allowed_site_ids = get_user_site_ids(user, db)
    if not allowed_site_ids:
        raise HTTPException(status_code=403, detail="No site access assigned for this user")

    site_check_time = time.time()
    logger.info(f"[2] Site access check: {(site_check_time - auth_time)*1000:.2f}ms - {len(allowed_site_ids)} sites")

    # Calculate aggregates using a single efficient query
    aggregates_start = time.time()

    # Build aggregate query with only site-based filtering
    aggregate_query = db.query(
        # Count aggregates using CASE statements (conditional counting)
        func.count(case((and_(Lead.HealthScore < 40, Lead.OverdueDays > 3), 1))).label('urgentCount'),
        func.count(case((Lead.FollowUpStatus == 'today', 1))).label('dueTodayCount'),
        func.count(case((Lead.BuyingIntent >= 8, 1))).label('highIntentCount'),
        func.count(case((Lead.FollowUpStatus == 'overdue', 1))).label('overdueCount'),
        func.count(case((Lead.ChurnRisk == 'critical', 1))).label('criticalChurnCount'),
        func.count(case((Lead.ChurnRisk == 'high', 1))).label('highChurnCount'),
        # Average aggregates
        func.avg(Lead.HealthScore).label('avgHealthScore'),
        func.avg(Lead.ConversionProbability).label('avgConversionProbability'),
        # Total count
        func.count(Lead.LeadId).label('totalCount')
    )

    # Apply only site-based filtering
    aggregate_query = aggregate_query.filter(Lead.SiteId.in_(allowed_site_ids))

    aggregate_result = aggregate_query.first()

    aggregates_end = time.time()
    logger.info(f"[3] Aggregates query execution: {(aggregates_end - aggregates_start)*1000:.2f}ms")

    aggregates = {
        "urgentCount": aggregate_result.urgentCount or 0,
        "dueTodayCount": aggregate_result.dueTodayCount or 0,
        "highIntentCount": aggregate_result.highIntentCount or 0,
        "overdueCount": aggregate_result.overdueCount or 0,
        "criticalChurnCount": aggregate_result.criticalChurnCount or 0,
        "highChurnCount": aggregate_result.highChurnCount or 0,
        "avgHealthScore": float(aggregate_result.avgHealthScore) if aggregate_result.avgHealthScore else 0,
        "avgConversionProbability": float(aggregate_result.avgConversionProbability) if aggregate_result.avgConversionProbability else 0,
        "totalCount": aggregate_result.totalCount or 0
    }

    total_time = time.time() - start_time
    logger.info(f"TOTAL REQUEST TIME: {total_time*1000:.2f}ms ({total_time:.2f}s)")
    logger.info("="*80)

    return {
        "aggregates": aggregates,
        "message": "Aggregates calculated successfully",
        "statusCode": 200
    }


