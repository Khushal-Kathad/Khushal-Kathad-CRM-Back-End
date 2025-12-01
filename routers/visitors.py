from string import ascii_uppercase
from tokenize import String
from sqlalchemy import cast, String, literal_column
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, HTTPException, status, Body
from pytz import timezone
from fastapi import Path
from pydantic import BaseModel,Field
from typing import Annotated
from sqlalchemy.orm import Session,joinedload, load_only
from sqlalchemy import  select, func
from database import SessionLocal
from models import Visitors, Visit, Contact, Site, Users, Infra, Lead
from .auth import get_current_user
from datetime import datetime
from schemas.schemas import VisitRequest, VisitorsRequest, VisitorCreate
from collections import defaultdict
from fastapi import Query
from routers.security_utils import get_user_site_ids


router = APIRouter(
    prefix="/visitors",
    tags = ['visitors']
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
async def read_visitors(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    visitors = db.query(Visitors).filter(Visitors.CreatedById == user.get('id')).all()
    if not visitors:
        raise HTTPException(status_code=404, detail="No visitors found")
    return visitors


@router.get("/getsinglevisitors/{visitors_id}", status_code=status.HTTP_200_OK )
async def read_visitors_by_id (user:user_dependency, db: db_dependency,visitors_id :int=Path(gt=0)):
    if user is None:
        raise HTTPException (status_code=401, detail='Authentication Failed')
    visitors = db.query(Visitors).filter(Visitors.VisitorsId == visitors_id) \
        .filter(Visitors.CreatedById == user.get('id')).first()
    if visitors is not None:
        return visitors
    raise HTTPException(status_code=404, detail='Visitors not found')



# @router.post("/CreatevisitorsandVisit", status_code=status.HTTP_201_CREATED)
# async def create_visitors_and_visit(user: user_dependency,db: db_dependency,visit_request: VisitRequest,visitors_request: VisitorsRequest):
#     if user is None:
#         raise HTTPException(status_code=401, detail='Authentication Failed')
#     visit_model = None
#     visit_id = visitors_request.VisitId
#
#     # Step 1: Check if VisitId is provided and fetch the Visit
#     if visit_id:
#         visit_model = db.query(Visit).filter(Visit.VisitId == visit_id).first()
#
#     # Step 2: If VisitId is not provided or invalid, check for an existing Visit with same fields
#     if not visit_model:
#         existing_visit = db.query(Visit).filter(
#             Visit.InfraId == visit_request.InfraId,
#             Visit.SiteId == visit_request.SiteId,
#             Visit.SalesPersonId == visit_request.SalesPersonId,
#             Visit.Purpose == visit_request.Purpose,
#             Visit.VisitStatus == visit_request.VisitStatus,
#             Visit.VisitOutlook == visit_request.VisitOutlook
#         ).first()
#
#         if existing_visit:
#             visit_model = existing_visit
#         else:
#             # Create a new Visit if none exists
#             visit_model = Visit(
#                 **visit_request.dict(),
#                 CreatedById=user.get('id'),
#                 CreatedDate=get_time(),
#                 UpdatedDate=get_time()
#             )
#             db.add(visit_model)
#             db.commit()
#             db.refresh(visit_model)
#
#     # Step 3: Create multiple Visitors records with the resolved VisitId
#     created_visitors = []
#
#     for visitor_data in visitors_request.Visitors:
#         visitor_model = Visitors(
#             **visitor_data.dict(exclude={"VisitId"}),
#             VisitId=visit_model.VisitId,
#             CreatedById=user.get('id'),
#             CreatedDate=get_time(),
#             UpdatedDate=get_time()
#         )
#         db.add(visitor_model)
#         db.commit()
#         db.refresh(visitor_model)
#
#         created_visitors.append({
#             "VisitId": visitor_model.VisitId,
#             "ContactId": visitor_model.ContactId,
#             "LeadId": visitor_model.LeadId,
#             "InfraUnitId": visitor_model.InfraUnitId,
#             "VisitType": visitor_model.VisitType,
#             "PropertyType": visitor_model.PropertyType,
#             "Bedrooms": visitor_model.Bedrooms,
#             "SizeSqFt": visitor_model.SizeSqFt,
#             "ViewType": visitor_model.ViewType,
#             "FloorPreference": visitor_model.FloorPreference,
#             "BuyingIntent": visitor_model.BuyingIntent,
#             "Notes": visitor_model.Notes,
#             "Direction": visitor_model.Direction,
#             "VisitorFeedback": visitor_model.VisitorFeedback,
#             "FollowUpDate": visitor_model.FollowUpDate,
#             "FollowUpStatus": visitor_model.FollowUpStatus,
#             "IsDeleted": visitor_model.IsDeleted
#         })
#
#     # Step 4: Prepare and return the response
#     return {
#         "Visitors": created_visitors,
#         "Visit": {
#             "InfraId": visit_model.InfraId,
#             "SiteId": visit_model.SiteId,
#             "VisitDate": visit_model.VisitDate,
#             "SalesPersonId": visit_model.SalesPersonId,
#             "Purpose": visit_model.Purpose,
#             "VisitStatus": visit_model.VisitStatus,
#             "VisitOutlook": visit_model.VisitOutlook
#         }
#     }


# OLD CODE - Kept for reference
# @router.post("/CreatevisitorsandVisit", status_code=status.HTTP_201_CREATED)
# async def create_visitors_and_visit(
#     user: user_dependency,
#     db: db_dependency,
#     visit_request: VisitRequest,
#     visitors_request: VisitorsRequest
# ):
#     if user is None:
#         raise HTTPException(status_code=401, detail='Authentication Failed')
#
#     visit_model = None
#     visit_id = visitors_request.VisitId
#
#     # Step 1: Check if VisitId is provided and fetch the Visit
#     if visit_id:
#         visit_model = db.query(Visit).filter(Visit.VisitId == visit_id).first()
#
#     # Step 2: If VisitId is not provided or invalid, always create a new Visit
#     if not visit_model:
#         visit_model = Visit(
#             **visit_request.dict(),
#             CreatedById=user.get('id'),
#             CreatedDate=get_time(),
#             UpdatedDate=get_time()
#         )
#         db.add(visit_model)
#         db.commit()
#         db.refresh(visit_model)
#
#     # Step 3: Create multiple Visitors records with the resolved VisitId
#     created_visitors = []
#
#     for visitor_data in visitors_request.Visitors:
#         visitor_model = Visitors(
#             **visitor_data.dict(exclude={"VisitId"}),
#             VisitId=visit_model.VisitId,
#             CreatedById=user.get('id'),
#             CreatedDate=get_time(),
#             UpdatedDate=get_time()
#         )
#         db.add(visitor_model)
#         db.commit()
#         db.refresh(visitor_model)
#
#         created_visitors.append({
#             "VisitId": visitor_model.VisitId,
#             "ContactId": visitor_model.ContactId,
#             "LeadId": visitor_model.LeadId,
#             "InfraUnitId": visitor_model.InfraUnitId,
#             "VisitType": visitor_model.VisitType,
#             "PropertyType": visitor_model.PropertyType,
#             "Bedrooms": visitor_model.Bedrooms,
#             "SizeSqFt": visitor_model.SizeSqFt,
#             "ViewType": visitor_model.ViewType,
#             "FloorPreference": visitor_model.FloorPreference,
#             "BuyingIntent": visitor_model.BuyingIntent,
#             "Notes": visitor_model.Notes,
#             "Direction": visitor_model.Direction,
#             "VisitorFeedback": visitor_model.VisitorFeedback,
#             "FollowUpDate": visitor_model.FollowUpDate,
#             "FollowUpStatus": visitor_model.FollowUpStatus,
#             "IsDeleted": visitor_model.IsDeleted
#         })
#
#     # Step 4: Prepare and return the response
#     return {
#         "Visitors": created_visitors,
#         "Visit": {
#             "InfraId": visit_model.InfraId,
#             "SiteId": visit_model.SiteId,
#             "VisitDate": visit_model.VisitDate,
#             "SalesPersonId": visit_model.SalesPersonId,
#             "Purpose": visit_model.Purpose,
#             "VisitStatus": visit_model.VisitStatus,
#             "VisitOutlook": visit_model.VisitOutlook
#         }
#     }


# NEW CODE - Creates Lead for each Visitor with BrokerId
@router.post("/CreatevisitorsandVisit", status_code=status.HTTP_201_CREATED)
async def create_visitors_and_visit(
    user: user_dependency,
    db: db_dependency,
    visit_request: VisitRequest = Body(...),
    visitors_request: VisitorsRequest = Body(...)
):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    # Step 1: Add site access security
    allowed_site_ids = get_user_site_ids(user, db)
    print(f"DEBUG: User ID: {user.get('id')}, Allowed Site IDs: {allowed_site_ids}")

    if not allowed_site_ids:
        raise HTTPException(status_code=403, detail="No site access assigned for this user")

    if visit_request.SiteId not in allowed_site_ids:
        raise HTTPException(status_code=403, detail=f"You don't have access to site {visit_request.SiteId}. Your allowed sites: {allowed_site_ids}")

    visit_model = None
    visit_id = visitors_request.VisitId

    # Step 2: Check if VisitId is provided and fetch the Visit
    if visit_id:
        visit_model = db.query(Visit).filter(Visit.VisitId == visit_id).first()

    # Step 3: If VisitId is not provided or invalid, create a new Visit
    if not visit_model:
        visit_model = Visit(
            **visit_request.dict(),
            CreatedById=user.get('id'),
            CreatedDate=get_time(),
            UpdatedDate=get_time()
        )
        db.add(visit_model)
        db.commit()
        db.refresh(visit_model)

    # Step 4: Create all Visitors first (without LeadId)
    created_visitors = []

    for visitor_data in visitors_request.Visitors:
        visitor_model = Visitors(
            **visitor_data.dict(exclude={"VisitId", "LeadId"}),
            VisitId=visit_model.VisitId,
            LeadId=None,  # Will update later after Lead creation
            CreatedById=user.get('id'),
            CreatedDate=get_time(),
            UpdatedDate=get_time()
        )
        db.add(visitor_model)
        db.commit()
        db.refresh(visitor_model)
        created_visitors.append(visitor_model)

    # Step 5: Find Broker from the created visitors
    contact_ids = [v.ContactId for v in created_visitors if v.ContactId]
    broker_id = None

    if contact_ids:
        broker_contact = db.query(Contact).filter(
            Contact.ContactId.in_(contact_ids),
            Contact.ContactType == 'Broker'
        ).first()

        if broker_contact:
            broker_id = broker_contact.ContactId

    # Step 6: Create Lead only for visitors with ContactType "Customer"
    for visitor_model in created_visitors:
        # Generate LeadName and check ContactType
        contact_name = "Unknown"
        should_create_lead = False

        if visitor_model.ContactId:
            contact = db.query(Contact).filter(
                Contact.ContactId == visitor_model.ContactId
            ).first()
            if contact:
                contact_name = f"{contact.ContactFName} {contact.ContactLName}".strip()
                # Only create lead if ContactType is "Customer"
                if contact.ContactType == "Customer":
                    should_create_lead = True

        # Only create lead for Customer contacts
        if should_create_lead:
            # lead_name = f"Lead-{contact_name}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            lead_name = contact_name

            # Create Lead
            lead_model = Lead(
                LeadName=lead_name,
                ContactId=visitor_model.ContactId,
                SiteId=visit_model.SiteId,
                InfraId=visit_model.InfraId,
                InfraUnitId=visitor_model.InfraUnitId,
                Bedrooms=visitor_model.Bedrooms,
                SizeSqFt=visitor_model.SizeSqFt,
                ViewType=visitor_model.ViewType,
                FloorPreference=visitor_model.FloorPreference,
                BuyingIntent=visitor_model.BuyingIntent,
                Direction=visitor_model.Direction,
                LeadStatus="New",
                LeadType="Walk-in",
                LeadSource="Site Visit",
                LeadNotes=visitor_model.Notes,
                SuggestedUnitId=visitor_model.InfraUnitId,
                BrokerId=broker_id,
                CreatedById=user.get('id'),
                CreatedDate=get_time(),
                UpdatedDate=get_time()
            )
            db.add(lead_model)
            db.commit()
            db.refresh(lead_model)

            # Update Visitor with LeadId
            visitor_model.LeadId = lead_model.LeadId
            db.add(visitor_model)
            db.commit()

    # Step 7: Prepare response
    response_visitors = []
    for visitor_model in created_visitors:
        response_visitors.append({
            "VisitorsId": visitor_model.VisitorsId,
            "VisitId": visitor_model.VisitId,
            "LeadId": visitor_model.LeadId,
            "ContactId": visitor_model.ContactId,
            "InfraUnitId": visitor_model.InfraUnitId,
            "VisitType": visitor_model.VisitType,
            "PropertyType": visitor_model.PropertyType,
            "Bedrooms": visitor_model.Bedrooms,
            "SizeSqFt": visitor_model.SizeSqFt,
            "ViewType": visitor_model.ViewType,
            "FloorPreference": visitor_model.FloorPreference,
            "BuyingIntent": visitor_model.BuyingIntent,
            "Notes": visitor_model.Notes,
            "Direction": visitor_model.Direction,
            "VisitorFeedback": visitor_model.VisitorFeedback,
            "FollowUpDate": visitor_model.FollowUpDate,
            "FollowUpStatus": visitor_model.FollowUpStatus,
            "IsDeleted": visitor_model.IsDeleted
        })

    return {
        "Visitors": response_visitors,
        "Visit": {
            "VisitId": visit_model.VisitId,
            "InfraId": visit_model.InfraId,
            "SiteId": visit_model.SiteId,
            "VisitDate": visit_model.VisitDate,
            "SalesPersonId": visit_model.SalesPersonId,
            "Purpose": visit_model.Purpose,
            "VisitStatus": visit_model.VisitStatus,
            "VisitOutlook": visit_model.VisitOutlook
        }
    }





@router.put("/VisitorsUpdate/{visitors_id}",status_code=status.HTTP_204_NO_CONTENT )
async def update_Visitors (user: user_dependency,db: db_dependency,visitors_id: int ,visitors_request:VisitorCreate):
    if user is None:
        raise HTTPException (status_code=401, detail='Authentication Failed')

    # Get allowed site IDs for the user
    allowed_site_ids = get_user_site_ids(user, db)
    if not allowed_site_ids:
        raise HTTPException(status_code=403, detail="No site access assigned for this user")

    # Query visitor with site permission check through Visit relationship
    visitors_model = db.query(Visitors).join(Visit).filter(
        Visitors.VisitorsId == visitors_id,
        Visit.SiteId.in_(allowed_site_ids)
    ).first()

    if visitors_model is None:
        raise HTTPException(status_code=404, detail="Visitors not found")
    visitors_model.ContactId = visitors_request.ContactId
    visitors_model.LeadId = visitors_request.LeadId
    visitors_model.InfraUnitId = visitors_request.InfraUnitId
    visitors_model.VisitType = visitors_request.VisitType
    visitors_model.PropertyType = visitors_request.PropertyType
    visitors_model.Bedrooms = visitors_request.Bedrooms
    visitors_model.SizeSqFt = visitors_request.SizeSqFt
    visitors_model.ViewType = visitors_request.ViewType
    visitors_model.FloorPreference = visitors_request.FloorPreference
    visitors_model.BuyingIntent = visitors_request.BuyingIntent
    # visitors_model.VisitStatus = visitors_request.VisitStatus
    visitors_model.Notes = visitors_request.Notes
    visitors_model.Direction = visitors_request.Direction
    visitors_model.VisitorFeedback = visitors_request.VisitorFeedback
    visitors_model.FollowUpDate = visitors_request.FollowUpDate
    visitors_model.FollowUpStatus = visitors_request.FollowUpStatus
    visitors_model.IsDeleted = visitors_request.IsDeleted
    # visitors_model.VisitOutlook = visitors_request.VisitOutlook
    visitors_model.UpdatedDate = get_time()
    db.add(visitors_model)
    db.commit()





@router.delete("/visitorsDelete/{visitors_id}", status_code=status.HTTP_204_NO_CONTENT )
async def delete_visitors (user:user_dependency, db: db_dependency,visitors_id: int =Path(gt=0)):
    if user is None:
        raise HTTPException (status_code=401, detail='Authentication Failed')
    visitors_model = db.query(Visitors).filter(Visitors.VisitorsId == visitors_id).filter(Visitors.CreatedById == user.get('id')).first()
    if visitors_model is None:
        raise HTTPException(status_code=404, detail="visitors not found")
    db.query(Visitors).filter(Visitors.VisitorsId == visitors_id).delete()
    db.commit()


@router.get("/Visitors_full_details/", status_code=status.HTTP_200_OK )
async def read_visitors_full_details (user:user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException (status_code=401, detail='Authentication Failed')
    visitors_details = db.query(Visitors).options(joinedload(Visitors.visit), joinedload(Visitors.contacts).load_only(Contact.ContactFName,
                       Contact.ContactLName, Contact.ContactEmail, Contact.ContactNo)).all()
    return visitors_details



@router.get("/visitors_leads/{lead_id}", status_code=status.HTTP_200_OK )
async def read_visitors_leads (user:user_dependency, db: db_dependency, lead_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException (status_code=401, detail='Authentication Failed')
    visitors_model = db.query(Visitors).filter(Visitors.LeadId == lead_id).all()
    if visitors_model is not None:
        return visitors_model
    raise HTTPException(status_code=404, detail = 'visitors not found')


@router.get("/visitors_report/", status_code=status.HTTP_200_OK )
async def read_visitors_report (user:user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException (status_code=401, detail='Authentication Failed')
    visitors_counts = (
        db.query(Visitors.VisitType, func.count(Visitors.VisitId)).filter(Visitors.VisitType.in_(["New Visit", "Re-visit"]))
        .group_by(Visitors.VisitType).all()
    )
    response = {
        "New Visit": 0,
        "Re-visit": 0
    }
    for visit_type, count in visitors_counts:
        response[visit_type] = count
    return response



@router.get("/Visitors_full_details/{visitors_id}", status_code=status.HTTP_200_OK )
async def read_visitors_full_details_by_id (user:user_dependency, db: db_dependency, visitors_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException (status_code=401, detail='Authentication Failed')
    visitors_details = db.query(Visitors).options(joinedload(Visitors.contacts).load_only(Contact.ContactFName,
                     Contact.ContactLName,Contact.ContactEmail,Contact.ContactNo),\
                     joinedload(Visitors.lead),
                     # joinedload(Visit.site),
                     # joinedload(Visit.infra),
                     joinedload(Visitors.infraunit),
                     # joinedload(Visit.broker),
                     joinedload(Visitors.created_by)
    ).filter(
        Visitors.VisitorsId == visitors_id,
        Visitors.CreatedById == user.get('id')
    ).first()
    if visitors_details is not None:
        return visitors_details
    raise HTTPException(status_code=404, detail='visit not found')

#
# @router.get("/visitors_and_visit_leads/{lead_id}", status_code=status.HTTP_200_OK )
# async def read_visitors_and_visit_leads (user:user_dependency, db: db_dependency, lead_id: int = Path(gt=0)):
#     if user is None:
#         raise HTTPException (status_code=401, detail='Authentication Failed')
#     visitors_model = db.query(Visitors).filter(Visitors.LeadId == lead_id).all()
#     db.query(Visitors).options(joinedload(Visitors.visit).load_only((Visit.InfraId, Visit.SiteId, Visit.VisitDate, Visit.SalesPersonId, Visit.Purpose)))
#     if visitors_model is not None:
#         return visitors_model
#     raise HTTPException(status_code=404, detail = 'visitors not found')


@router.get("/visitors_and_visit_leads/{lead_id}", status_code=status.HTTP_200_OK)
async def read_visitors_and_visit_leads(user: user_dependency, db: db_dependency, lead_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    visitors_model = db.query(Visitors).options(
        joinedload(Visitors.visit).load_only(
            Visit.InfraId,
            Visit.SiteId,
            Visit.VisitDate,
            Visit.SalesPersonId,
            Visit.Purpose
        )
    ).filter(Visitors.LeadId == lead_id).all()

    if visitors_model:
        return visitors_model

    raise HTTPException(status_code=404, detail='visitors not found')




# @router.get(
#     "/visit_with_visitors/{visit_id}",status_code=status.HTTP_200_OK)
# async def get_visit_with_visitors(user: user_dependency,db: db_dependency,visit_id: int = Path(gt=0, description="Visit ID")):
#     if user is None:
#         raise HTTPException(status_code=401, detail="Authentication Failed")
#     # Fetch the visit
#     visit = db.query(Visit).filter(Visit.VisitId == visit_id).first()
#     if not visit:
#         raise HTTPException(status_code=404, detail="Visit not found")
#
#     # Fetch associated visitors with contact details
#     visitors = db.query(Visitors).options(
#         joinedload(Visitors.contacts).load_only(Contact.ContactFName, Contact.ContactLName, Contact.ContactId, Contact.ContactNo)  # lazy load Contact relationship
#     ).filter(Visitors.VisitId == visit_id).all()
#
#     # Return combined response
#     return {
#         "visit": visit,
#         "visitors": visitors
#     }


# @router.get( "/visit_with_visitors/{visit_id}", status_code=status.HTTP_200_OK)
# async def get_visit_with_visitors(user: user_dependency,db: db_dependency,visit_id: int = Path(gt=0, description="Visit ID")):
#     if user is None:
#         raise HTTPException(status_code=401, detail="Authentication Failed")
#
#     # Fetch the visit with related Site, Infra, CreatedBy user
#     visit = db.query(Visit).options(
#         joinedload(Visit.site).load_only(
#             Site.SiteId, Site.SiteName, Site.SiteAddress
#         ),
#         joinedload(Visit.infra).load_only(
#             Infra.InfraId, Infra.InfraName, Infra.InfraCategory
#         ),
#         joinedload(Visit.created_by).load_only(
#             Users.id, Users.FirstName, Users.LastName
#         ),
#         # You can add more joinedloads like lead, broker, infraunit if needed
#     ).filter(Visit.VisitId == visit_id).first()
#
#     if not visit:
#         raise HTTPException(status_code=404, detail="Visit not found")
#
#     # Fetch associated visitors with contact details
#     visitors = db.query(Visitors).options(
#         joinedload(Visitors.contacts).load_only(
#             Contact.ContactId, Contact.ContactFName, Contact.ContactLName, Contact.ContactType, Contact.ContactNo
#         )
#     ).filter(Visitors.VisitId == visit_id).all()
#
#     return {
#         "visit": visit,
#         "visitors": visitors
#     }


@router.get("/visit_with_visitors/{visit_id}", status_code=status.HTTP_200_OK)
async def get_visit_with_visitors( user: user_dependency,db: db_dependency,visit_id: int = Path(gt=0, description="Visit ID")):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    # Fetch the visit with related Site, Infra, CreatedBy user
    visit = (
        db.query(Visit)
        .options(
            joinedload(Visit.site).load_only(
                Site.SiteId, Site.SiteName, Site.SiteAddress
            ),
            joinedload(Visit.infra).load_only(
                Infra.InfraId, Infra.InfraName, Infra.InfraCategory
            ),
            joinedload(Visit.created_by).load_only(
                Users.id, Users.FirstName, Users.LastName
            ),
        )
        .filter(Visit.VisitId == visit_id)
        .first()
    )

    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")

    # Fetch associated visitors with contact details (exclude deleted)
    visitors = (
        db.query(Visitors)
        .options(
            joinedload(Visitors.contacts).load_only(
                Contact.ContactId,
                Contact.ContactFName,
                Contact.ContactLName,
                Contact.ContactType,
                Contact.ContactNo,
            )
        )
        .filter(
            Visitors.VisitId == visit_id,
            Visitors.IsDeleted == "No"   # only active visitors
        )
        .all()
    )

    return {
        "visit": visit,
        "visitors": visitors,
    }
