from fastapi import APIRouter, Depends, HTTPException,status, Query
from pytz import timezone
from fastapi import Path
from pydantic import BaseModel,Field
from models import Lead,Contact, ProspectType, Site
from typing import Annotated, Optional
from sqlalchemy.orm import Session,joinedload, load_only
from sqlalchemy import select, func, String
from database import SessionLocal
from .auth import get_current_user
from datetime import datetime
from schemas.schemas import ContactRequest
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_

# import redis  # Commented out - not currently used
import json
import time


router = APIRouter(
    prefix="/contact",
    tags = ['contact']
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


# @router.get("/")
# async def read_contact(user:user_dependency, db: db_dependency):
#     if user is None:
#         raise HTTPException (status_code=401, detail='Authentication Failed')
#     return db.query(Contact).all()


# @router.get("/")
# async def read_contact(user: user_dependency, db: db_dependency):
#     if user is None:
#         raise HTTPException(status_code=401, detail='Authentication Failed')
#     lead_counts_subq = (
#         db.query(
#             Lead.ContactId.label("contactid"),
#             func.count().label("leadcount")
#         )
#         .group_by(Lead.ContactId)
#         .subquery()
#     )
#     result = (
#         db.query(
#             Contact,
#             func.coalesce(lead_counts_subq.c.leadcount, 0).label("leadcount")
#         )
#         .outerjoin(lead_counts_subq, Contact.ContactId == lead_counts_subq.c.contactid)
#         .order_by(func.coalesce(lead_counts_subq.c.leadcount, 0).desc())
#         .all()
#     )
#     response = [
#         {
#             **contact.__dict__,
#             "leadcount": leadcount
#         }
#         for contact, leadcount in result
#     ]
#     for item in response:
#         item.pop('_sa_instance_state', None)
#     return response


from fastapi import Query
#
# @router.get("/")
# async def read_contact(
#     user: user_dependency,
#     db: db_dependency,
#     sIndex: int = Query(1, alias="sIndex"),  # Start index (1-based)
#     limit: int = Query(20)
# ):
#     if user is None:
#         raise HTTPException(status_code=401, detail='Authentication Failed')
#
#     # Convert 1-based index to 0-based offset
#     offset = max(sIndex - 1, 0)
#     print(offset)
#
#     lead_counts_subq = (
#         db.query(
#             Lead.ContactId.label("contactid"),
#             func.count().label("leadcount")
#         )
#         .group_by(Lead.ContactId)
#         .subquery()
#     )
#
#     total_records = db.query(Contact).count()
#
#     result = (
#         db.query(
#             Contact,
#             func.coalesce(lead_counts_subq.c.leadcount, 0).label("leadcount")
#         )
#         .outerjoin(lead_counts_subq, Contact.ContactId == lead_counts_subq.c.contactid)
#         .order_by(func.coalesce(lead_counts_subq.c.leadcount, 0).desc())
#         .offset(offset)
#         .limit(limit)
#         .all()
#     )
#
#     response = [
#         {
#             **contact.__dict__,
#             "leadcount": leadcount
#         }
#         for contact, leadcount in result
#     ]
#
#     for item in response:
#         item.pop('_sa_instance_state', None)
#
#     next_index = sIndex + limit
#     if next_index > total_records:
#         next_index = 1  # Loop back to beginning
#
#     return {
#         "data": response,
#         "count": len(response),
#         "total_records": total_records,
#         "sIndex": sIndex,
#         "limit": limit,
#         "nextIndex": next_index
#     }


# from sqlalchemy import func, or_, String

@router.get("/")
async def read_contact(user: user_dependency,db: db_dependency,sIndex: int = Query(1, alias="sIndex"),  # Start index (1-based)
    limit: int = Query(20),
    query: Optional[str] = Query(None),
    contact_type: Optional[str] = Query(None)
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    # ✅ Subquery for Customer lead counts (Lead.ContactId)
    customer_lead_counts_subq = (
        db.query(
            Lead.ContactId.label("contactid"),
            func.count().label("customer_leadcount")
        )
        .group_by(Lead.ContactId)
        .subquery()
    )

    # ✅ Subquery for Broker lead counts (Lead.BrokerId)
    broker_lead_counts_subq = (
        db.query(
            Lead.BrokerId.label("contactid"),
            func.count().label("broker_leadcount")
        )
        .group_by(Lead.BrokerId)
        .subquery()
    )

    # ✅ Step 1: Base query with filters
    contact_query = db.query(Contact)

    if query:
        contact_query = contact_query.filter(
            or_(
                Contact.ContactNo.ilike(f"%{query}%"),
                Contact.ContactFName.ilike(f"%{query}%"),
                Contact.ContactLName.ilike(f"%{query}%"),
                func.cast(Contact.ContactId, String).ilike(f"%{query}%"),
                (Contact.ContactFName + ' ' + Contact.ContactLName).ilike(f"%{query}%")
            )
        )

    if contact_type:
        contact_query = contact_query.filter(Contact.ContactType.ilike(f"%{contact_type}%"))

    total_records = contact_query.count()

    if total_records == 0:
        return {
            "data": [],
            "count": 0,
            "total_records": 0,
            "sIndex": 1,
            "limit": limit,
            "nextIndex": 1
        }

    offset = max(sIndex - 1, 0)
    if offset >= total_records:
        offset = 0
        sIndex = 1

    # ✅ Step 2: Join both subqueries
    result = (
        contact_query
        .outerjoin(customer_lead_counts_subq, Contact.ContactId == customer_lead_counts_subq.c.contactid)
        .outerjoin(broker_lead_counts_subq, Contact.ContactId == broker_lead_counts_subq.c.contactid)
        .add_columns(
            func.coalesce(customer_lead_counts_subq.c.customer_leadcount, 0).label("customer_leadcount"),
            func.coalesce(broker_lead_counts_subq.c.broker_leadcount, 0).label("broker_leadcount")
        )
        .order_by(func.coalesce(customer_lead_counts_subq.c.customer_leadcount, 0).desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    # ✅ Step 3: Build response
    response = [
        {
            **contact.__dict__,
            "customer_leadcount": customer_leadcount,
            "broker_leadcount": broker_leadcount
        }
        for contact, customer_leadcount, broker_leadcount in result
    ]

    for item in response:
        item.pop("_sa_instance_state", None)

    next_index = sIndex + limit
    if next_index > total_records:
        next_index = 1

    return {
        "data": response,
        "count": len(response),
        "total_records": total_records,
        "sIndex": sIndex,
        "limit": limit,
        "nextIndex": next_index
    }





@router.get("/getsinglecontact/{contact_id}", status_code=status.HTTP_200_OK )
async def read_contact (user:user_dependency, db: db_dependency, contact_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException (status_code=401, detail='Authentication Failed')
    contact_model = db.query(Contact).filter(Contact.ContactId == contact_id).first()
    if contact_model is not None:
        return contact_model
    raise HTTPException(status_code=404, detail = 'contact not found')



# @router.post("/createcontact",status_code=status.HTTP_201_CREATED)
# async def create_contact(user: user_dependency, db: db_dependency,
#                        contact_request:ContactRequest):
#     if user is None:
#         raise HTTPException(status_code=401, detail='Authentication Failed')
#     contact_model = Contact(**contact_request.dict(), CreatedById=user.get('id'), CreatedDate=get_time(), UpdatedDate=get_time())
#     db.add(contact_model)
#     db.commit()
#     db.refresh(contact_model)
#     return {"ContactId" : contact_model.ContactId}


@router.post("/createcontact", status_code=status.HTTP_201_CREATED)
async def create_contact(user: user_dependency, db: db_dependency,
                         contact_request: ContactRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    # Check if ContactNo already exists
    existing_contact = db.query(Contact).filter(Contact.ContactNo == contact_request.ContactNo).first()
    if existing_contact:
        raise HTTPException(status_code=400, detail='Contact with this ContactNo already exists.')
    # Proceed to create new contact
    contact_model = Contact(**contact_request.dict(),
                            CreatedById=user.get('id'),
                            CreatedDate=get_time(),
                            UpdatedDate=get_time())
    db.add(contact_model)
    db.commit()
    db.refresh(contact_model)
    return {"ContactId": contact_model.ContactId}


@router.put("/updatecontact/{contact_id}", status_code=status.HTTP_204_NO_CONTENT )
async def update_contact (user: user_dependency,db: db_dependency,contact_id: int, contact_request:ContactRequest):
    if user is None:
        raise HTTPException (status_code=401, detail='Authentication Failed')
    existing_contact = db.query(Contact).filter(Contact.ContactId == contact_id).first()
    if existing_contact is None:
        raise HTTPException (status_code=404, detail="contact not found")

        # Check if ContactNo already exists for a different contact
    duplicate_contact = db.query(Contact).filter(
    Contact.ContactNo == contact_request.ContactNo,Contact.ContactId != contact_id).first()
    if duplicate_contact:
        raise HTTPException(status_code=400, detail="Another contact with this ContactNo already exists.")
    # print(contact_request.ContactFName)
    existing_contact.ContactFName = contact_request.ContactFName
    # print(existing_contact.ContactFName)
    existing_contact.ContactLName =contact_request.ContactLName
    existing_contact.ContactEmail =contact_request.ContactEmail
    existing_contact.ContactNo =contact_request.ContactNo
    existing_contact.ContactCity = contact_request.ContactCity
    existing_contact.ContactState = contact_request.ContactState
    existing_contact.ContactAddress =contact_request.ContactAddress
    existing_contact.ContactPostalCode = contact_request.ContactPostalCode
    existing_contact.ContactCountryCode  = contact_request.ContactCountryCode
    db.add(existing_contact)
    db.commit()




@router.delete("/deletecontact/{contact_id}", status_code=status.HTTP_204_NO_CONTENT )
async def delete_contact (user:user_dependency, db: db_dependency, contact_id : int =Path(gt=0)):
    if user is None:
        raise HTTPException (status_code=401, detail='Authentication Failed')
    contact_model = db.query(Contact).filter(Contact.ContactId==contact_id).first()
    if contact_model is None:
        raise HTTPException (status_code=404, detail="contact not found")
    try:
        db.query(Contact).filter(Contact.ContactId == contact_id).delete()
        db.commit()
    except IntegrityError:
        db.rollback()  # Rollback the session to maintain integrity
        raise HTTPException(status_code=400,
                            detail="Bad Request: Cannot delete contact because it is referenced by other records.")




# redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
# @router.get("/contact_search")
# async def contact_search(user: user_dependency, db: db_dependency, query: Optional[str] = Query(None),
#                          contact_type: Optional[str] = Query(None)):
#     if user is None:
#         raise HTTPException(status_code=401, detail="Authentication Failed")
#
#     cache_key = f"contact_search:{query}:{contact_type}"
#     print(f"Checking Redis cache for key: {cache_key}")
#
#     # Start measuring cache lookup time
#     cache_start_time = time.perf_counter_ns()
#     cached_data = redis_client.get(cache_key)
#     cache_elapsed_time = (time.perf_counter_ns() - cache_start_time) // 1_000  # Convert to microseconds
#
#     if cached_data:
#         print(f"Fetching from Cache... Time taken: {cache_elapsed_time} µs")
#         return json.loads(cached_data)
#
#     print(f"Cache miss. Fetching from Database... (Cache lookup took {cache_elapsed_time} µs)")
#
#     # Measure database query time
#     db_start_time = time.perf_counter_ns()
#     contact_query = db.query(Contact)
#
#     if query:
#         contact_query = contact_query.filter(
#             or_(
#                 Contact.ContactNo.ilike(f"%{query}%"),
#                 Contact.ContactFName.ilike(f"%{query}%"),
#                 Contact.ContactLName.ilike(f"%{query}%"),
#                 Contact.ContactId.ilike(f"%{query}%"),
#             )
#         )
#     if contact_type:
#         contact_query = contact_query.filter(Contact.ContactType.ilike(f"%{contact_type}%"))
#
#     contacts = contact_query.all()
#     db_elapsed_time = (time.perf_counter_ns() - db_start_time) // 1_000  # Convert to microseconds
#
#     print(f"Fetching from Database... Time taken: {db_elapsed_time} µs")
#
#     results = [
#         {
#             "type": "contact",
#             "data": {
#                 "ContactId": contact.ContactId,
#                 "ContactNo": contact.ContactNo,
#                 "ContactFName": contact.ContactFName,
#                 "ContactLName": contact.ContactLName,
#                 "ContactType": contact.ContactType
#             }
#         }
#         for contact in contacts
#     ]
#
#     if not results:
#         raise HTTPException(status_code=404, detail="Search not found")
#     redis_client.set(cache_key, json.dumps(results))
#     return results





@router.get("/contact_search")
async def contact_search(user:user_dependency,db: db_dependency,query: Optional[str] = Query(None),
                         contact_type: Optional[str] = Query(None)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    contact_query = db.query(Contact)
    if query:
        contact_query = contact_query.filter(
            or_(
                Contact.ContactNo.ilike(f"%{query}%"),
                Contact.ContactFName.ilike(f"%{query}%"),
                Contact.ContactLName.ilike(f"%{query}%"),
                Contact.ContactId.ilike(f"%{query}%"),
                (Contact.ContactFName + ' ' + Contact.ContactLName).ilike(f"%{query}%")

            )
        )
    if contact_type:
        contact_query = contact_query.filter(Contact.ContactType.ilike(f"%{contact_type}%"))
    contacts = contact_query.all()
    results = [
        {
            "type": "contact",
            "data": {
                "ContactId": contact.ContactId,
                "ContactNo": contact.ContactNo,
                "ContactFName": contact.ContactFName,
                "ContactLName": contact.ContactLName,
                "ContactType": contact.ContactType

            }
        }
        for contact in contacts
    ]
    # if not results:
        # raise HTTPException(status_code=404, detail="Search not found")
    return results



@router.get("/count/{statustext}")
async def get_lead_count_by_contactId(user: user_dependency,db: db_dependency, statustext: str,contact_id: int = Query(..., alias="ContactId")):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    lead_count = db.query(Lead).filter(
        Lead.LeadStatus == statustext,
        Lead.ContactId == contact_id
    ).count()
    return {"lead_count": lead_count}






@router.get("/sitewisecount/")
async def get_lead_count_by_site_and_contact( user: user_dependency, db: db_dependency,contact_id: int = Query(..., alias="ContactId")):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    query = (
        db.query(
            Site.SiteName,
            Lead.LeadStatus,
            func.count(Lead.LeadId).label("lead_count")
        )
        .join(Lead, Site.SiteId == Lead.SiteId)
        .filter(Lead.ContactId == contact_id)
        .group_by(Site.SiteName, Lead.LeadStatus)
    )

    result = query.all()

    output = {}
    for site_name, lead_status, lead_count in result:
        if site_name not in output:
            output[site_name] = {}
        output[site_name][lead_status] = lead_count

    return output
