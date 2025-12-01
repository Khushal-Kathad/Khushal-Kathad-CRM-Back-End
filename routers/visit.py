from string import ascii_uppercase
from tokenize import String
from sqlalchemy import cast, String, literal_column, or_, and_
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, HTTPException,status
from pytz import timezone
from fastapi import Path
from pydantic import BaseModel,Field
# from models import Lead, Contact, ProspectType, Site
from typing import Annotated, Optional
from sqlalchemy.orm import Session,joinedload, load_only, aliased
from sqlalchemy import  select, func
from database import SessionLocal
from models import Visit, Contact, Lead, Infra, Site, InfraUnit, Visitors, Users, ProspectType
from .auth import get_current_user
from datetime import datetime
from schemas.schemas import VisitRequest
from collections import defaultdict
from fastapi import Query
from routers.security_utils import get_user_site_ids


router = APIRouter(
    prefix="/visit",
    tags = ['visit']
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
async def read_visit(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    allowed_site_ids = get_user_site_ids(user, db)
    if not allowed_site_ids:
        raise HTTPException(status_code=403, detail="No site access assigned for this user")
    visits = db.query(Visit).filter(Visit.SiteId.in_(allowed_site_ids)).all()
    return visits



@router.get("/get_single_visit/{visit_id}", status_code=status.HTTP_200_OK )
async def read_visit_by_id (user:user_dependency, db: db_dependency, visit_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException (status_code=401, detail='Authentication Failed')
    visit_model = db.query(Visit).filter(Visit.VisitId == visit_id).first()
    if visit_model is not None:
        return visit_model
    raise HTTPException(status_code=404, detail = 'visit not found')


# @router.post("/create_visit",status_code=status.HTTP_201_CREATED)
# async def create_visit(user: user_dependency, db: db_dependency,
#                        visit_request:VisitRequest):
#     if user is None:
#         raise HTTPException(status_code=401, detail='Authentication Failed')
#     visit_model = Visit(**visit_request.dict(), CreatedById=user.get('id'), CreatedDate=get_time(), UpdatedDate=get_time())
#     db.add(visit_model)
#     db.commit()
#     db.refresh(visit_model)
#     return {"VisitId": visit_model.VisitId}


@router.put("/updatevisit/{visit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_visit(user: user_dependency, db: db_dependency, visit_id: int, visit_request:VisitRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    visit_exist = db.query(Visit).filter(Visit.VisitId == visit_id ).first()
    if visit_exist is None:
        raise HTTPException(status_code=404, detail="visit detail not found")
    # visit_exist.ContactId=visit_request.ContactId
    # visit_exist.BrokerId=visit_request.BrokerId
    visit_exist.InfraId=visit_request.InfraId
    visit_exist.SiteId=visit_request.SiteId
    # visit_exist.InfraUnitId=visit_request.InfraUnitId
    # visit_exist.VisitType=visit_request.VisitType
    # visit_exist.PropertyType=visit_request.PropertyType
    # visit_exist.Bedrooms=visit_request.Bedrooms
    # visit_exist.SizeSqFt=visit_request.SizeSqFt
    # visit_exist.ViewType=visit_request.ViewType
    # visit_exist.FloorPreference=visit_request.FloorPreference
    # visit_exist.BuyingIntent=visit_request.BuyingIntent
    visit_exist.VisitDate=visit_request.VisitDate
    visit_exist.VisitStatus=visit_request.VisitStatus
    visit_exist.SalesPersonId=visit_request.SalesPersonId
    visit_exist.Purpose=visit_request.Purpose
    # visit_exist.Notes=visit_request.Notes
    # visit_exist.VisitorFeedback=visit_request.VisitorFeedback
    # visit_exist.FollowUpDate=visit_request.FollowUpDate
    # visit_exist.FollowUpStatus=visit_request.FollowUpStatus
    # visit_exist.CreatedDate=visit_request.CreatedDate
    visit_exist.UpdatedDate=get_time()
    visit_exist.VisitOutlook=visit_request.VisitOutlook
    # visit_exist.LeadId=visit_request.LeadId
    # visit_exist.CreatedById=visit_request.CreatedById
    db.add(visit_exist)
    db.commit()


@router.delete("/deletevisit/{visit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_visit (user: user_dependency, db: db_dependency, visit_id : int =Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    visit_model = db.query(Visit).filter(Visit.VisitId == visit_id).first()
    if visit_model is None:
        raise HTTPException(status_code=404, detail="visit detail not found")
    db.query(Visit).filter(Visit.VisitId == visit_id).delete()
    db.commit()


@router.patch("/SoftDeleteVisit/{visit_id}", status_code=status.HTTP_200_OK)
async def soft_delete_visit(user: user_dependency, db: db_dependency, visit_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    allowed_site_ids = get_user_site_ids(user, db)
    if not allowed_site_ids:
        raise HTTPException(status_code=403, detail="No site access assigned for this user")

    visit_model = db.query(Visit).filter(Visit.VisitId == visit_id, Visit.SiteId.in_(allowed_site_ids)).first()
    if visit_model is None:
        raise HTTPException(status_code=404, detail="Visit not found")

    if visit_model.IsDeleted == 1:
        raise HTTPException(status_code=400, detail="Visit is already deleted")

    visit_model.IsDeleted = 1
    visit_model.UpdatedDate = get_time()
    db.commit()

    return {
        "message": "Visit soft deleted successfully",
        "VisitId": visit_id,
        "statusCode": 200
    }





# @router.get("/visit_leads/{lead_id}", status_code=status.HTTP_200_OK )
# async def read_visit_leads (user:user_dependency, db: db_dependency, lead_id: int = Path(gt=0)):
#     if user is None:
#         raise HTTPException (status_code=401, detail='Authentication Failed')
#     visit_model = db.query(Visit).filter(Visit.LeadId == lead_id).all()
#     if visit_model is not None:
#         return visit_model
#     raise HTTPException(status_code=404, detail = 'visit not found')



# @router.get("/visitors_report/", status_code=status.HTTP_200_OK )
# async def read_visitors_report (user:user_dependency, db: db_dependency):
#     if user is None:
#         raise HTTPException (status_code=401, detail='Authentication Failed')
#     visitors_counts = (
#         db.query(Visitors.VisitType, func.count(Visitors.VisitId)).filter(Visitors.VisitType.in_(["New Visit", "Re-visit", "Direct Visit"]))
#         .group_by(Visitors.VisitType).all()
#     )
#     response = {
#         "New Visit": 0,
#         "Re-visit": 0,
#         "Direct Visit": 0
#     }
#     for visit_type, count in visitors_counts:
#         response[visit_type] = count
#     return response


@router.get("/Visit_full_details/", status_code=status.HTTP_200_OK)
async def read_visit_full_details(
        user: user_dependency,
        db: db_dependency,
        sIndex: int = Query(1, alias="sIndex"),
        limit: int = Query(20),
        VisitStatus: Optional[list[str]] = Query(None),
        VisitOutlook: Optional[list[str]] = Query(None),
        Purpose: Optional[list[str]] = Query(None),
        SiteName: Optional[list[str]] = Query(None),
        StartDate: Optional[str] = Query(None),
        EndDate: Optional[str] = Query(None),
        BrokerName: Optional[list[str]] = Query(None),
        BrokerNumber: Optional[list[str]] = Query(None),
        CustomerName: Optional[list[str]] = Query(None),
        CustomerNo: Optional[list[str]] = Query(None)
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    allowed_site_ids = get_user_site_ids(user, db)
    if not allowed_site_ids:
        raise HTTPException(status_code=403, detail="No site access assigned for this user")

    # Convert 1-based index to 0-based offset
    offset = max(sIndex - 1, 0) * limit

    # Create aliases for joining tables
    BrokerContact = aliased(Contact)
    CustomerContact = aliased(Contact)

    # Apply site filter to the query
    query = db.query(Visit).filter(Visit.SiteId.in_(allowed_site_ids))

    # Track if any filter was applied and which joins are needed
    filter_applied = False
    visitors_joined = False
    lead_joined = False
    broker_joined = False
    customer_joined = False
    prospect_joined = False
    site_joined = False

    # Apply filters
    # Visit table filters
    if VisitStatus:
        filter_applied = True
        query = query.filter(Visit.VisitStatus.in_(VisitStatus))

    if VisitOutlook:
        filter_applied = True
        query = query.filter(Visit.VisitOutlook.in_(VisitOutlook))

    if Purpose:
        filter_applied = True
        query = query.filter(Visit.Purpose.in_(Purpose))

    if SiteName:
        filter_applied = True
        if not site_joined:
            query = query.join(Visit.site)
            site_joined = True
        query = query.filter(
            or_(*[Site.SiteName.ilike(f"%{name}%") for name in SiteName])
        )

    if StartDate and EndDate:
        filter_applied = True
        try:
            start_date = datetime.strptime(StartDate, "%Y-%m-%d")
            end_date = datetime.strptime(EndDate, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
            query = query.filter(
                and_(
                    Visit.VisitDate >= start_date,
                    Visit.VisitDate <= end_date
                )
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid date format. Use YYYY-MM-DD. Error: {str(e)}")
    elif StartDate:
        filter_applied = True
        try:
            start_date = datetime.strptime(StartDate, "%Y-%m-%d")
            query = query.filter(Visit.VisitDate >= start_date)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid date format. Use YYYY-MM-DD. Error: {str(e)}")
    elif EndDate:
        filter_applied = True
        try:
            end_date = datetime.strptime(EndDate, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
            query = query.filter(Visit.VisitDate <= end_date)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid date format. Use YYYY-MM-DD. Error: {str(e)}")

    # Filter by Broker Name - uses Visitors → Contact join
    if BrokerName:
        filter_applied = True
        name_conditions = []
        for name in BrokerName:
            name = name.strip()
            if not name:
                continue
            name_conditions.append(
                or_(
                    Contact.ContactFName.ilike(f"%{name}%"),
                    Contact.ContactLName.ilike(f"%{name}%"),
                    (Contact.ContactFName + ' ' + Contact.ContactLName).ilike(f"%{name}%")
                )
            )

        if name_conditions:
            broker_visit_ids = (
                db.query(Visitors.VisitId)
                .join(Contact, Visitors.ContactId == Contact.ContactId)
                .filter(
                    Contact.ContactId.isnot(None),  # Ensure ContactId exists
                    Contact.ContactType == 'Broker',
                    or_(*name_conditions)
                )
                .distinct()
            )
            query = query.filter(Visit.VisitId.in_(broker_visit_ids))

    # Filter by Broker Number
    if BrokerNumber:
        filter_applied = True
        broker_visit_ids = (
            db.query(Visitors.VisitId)
            .join(Contact, Visitors.ContactId == Contact.ContactId)
            .filter(
                Contact.ContactId.isnot(None),  # Ensure ContactId exists
                Contact.ContactType == 'Broker',
                or_(*[cast(Contact.ContactNo, String).ilike(f"%{num}%") for num in BrokerNumber])
            )
            .distinct()
        )
        query = query.filter(Visit.VisitId.in_(broker_visit_ids))

    # Filter by Customer Name
    if CustomerName:
        filter_applied = True
        name_conditions = []
        for name in CustomerName:
            name = name.strip()
            if not name:
                continue
            name_conditions.append(
                or_(
                    Contact.ContactFName.ilike(f"%{name}%"),
                    Contact.ContactLName.ilike(f"%{name}%"),
                    (Contact.ContactFName + ' ' + Contact.ContactLName).ilike(f"%{name}%")
                )
            )

        if name_conditions:
            customer_visit_ids = (
                db.query(Visitors.VisitId)
                .join(Contact, Visitors.ContactId == Contact.ContactId)
                .filter(
                    Contact.ContactId.isnot(None),  # Ensure ContactId exists
                    Contact.ContactType == 'Customer',
                    or_(*name_conditions)
                )
                .distinct()
            )
            query = query.filter(Visit.VisitId.in_(customer_visit_ids))

    # Filter by Customer Number
    if CustomerNo:
        filter_applied = True
        customer_visit_ids = (
            db.query(Visitors.VisitId)
            .join(Contact, Visitors.ContactId == Contact.ContactId)
            .filter(
                Contact.ContactId.isnot(None),  # Ensure ContactId exists
                Contact.ContactType == 'Customer',
                or_(*[cast(Contact.ContactNo, String).ilike(f"%{num}%") for num in CustomerNo])
            )
            .distinct()
        )
        query = query.filter(Visit.VisitId.in_(customer_visit_ids))
    # Total records for pagination (after filters)
    total_records = query.count()

    # Check if no records found after filtering
    if filter_applied and total_records == 0:
        raise HTTPException(
            status_code=404,
            detail="No records found for the given filter(s)."
        )

    # Calculate total pages
    total_pages = (total_records + limit - 1) // limit if total_records > 0 else 1

    # If sIndex exceeds total pages, reset to last page
    if sIndex > total_pages:
        sIndex = total_pages
        offset = (sIndex - 1) * limit

    # Fetch paginated visit data
    visit_details = (
        query
        .options(
            joinedload(Visit.site).load_only(Site.SiteId, Site.SiteName, Site.SiteAddress),
            joinedload(Visit.infra).load_only(Infra.InfraId, Infra.InfraName, Infra.InfraCategory),
            joinedload(Visit.created_by).load_only(Users.id, Users.FirstName, Users.LastName),
        )
        .order_by(Visit.VisitDate.desc())  # Order by VisitDate descending (newest first)
        .offset(offset)
        .limit(limit)
        .all()
    )

    # Calculate next page index
    next_index = sIndex + 1 if sIndex < total_pages else 1

    # Fetch visitors for each visit and add VisitorName
    visit_ids = [visit.VisitId for visit in visit_details]

    # Query visitors with contact information using LEFT JOIN to include visitors without contacts
    # Include all visitors except those explicitly marked as deleted with "Yes"
    # Order by CreatedDate to get the earliest created visitor first
    visitors_data = (
        db.query(Visitors, Contact)
        .outerjoin(Contact, Visitors.ContactId == Contact.ContactId)
        .filter(Visitors.VisitId.in_(visit_ids))
        .filter(or_(Visitors.IsDeleted != "Yes", Visitors.IsDeleted == None))
        .order_by(Visitors.CreatedDate.asc())  # Order by CreatedDate ascending (earliest first)
        .all()
    )

    # Group visitors by VisitId - keep only the first visitor (earliest CreatedDate) per visit
    visitors_by_visit = {}
    seen_visits = set()  # Track which VisitIds we've already processed

    for visitor, contact in visitors_data:
        # Only process the first visitor for each VisitId (already ordered by CreatedDate asc)
        if visitor.VisitId not in seen_visits:
            seen_visits.add(visitor.VisitId)

            # Handle cases where contact might be None (no matching ContactId)
            if contact:
                visitor_name = f"{contact.ContactFName or ''} {contact.ContactLName or ''}".strip()
                contact_id = contact.ContactId
                contact_type = contact.ContactType
                contact_no = contact.ContactNo
            else:
                visitor_name = "Unknown Visitor"
                contact_id = visitor.ContactId
                contact_type = None
                contact_no = None

            visitors_by_visit[visitor.VisitId] = {
                "VisitorName": visitor_name,
                "ContactId": contact_id,
                "ContactType": contact_type,
                "ContactNo": contact_no
            }

    # Prepare response with visitor information
    response_data = []
    for visit in visit_details:
        visit_dict = {
            "VisitId": visit.VisitId,
            "InfraId": visit.InfraId,
            "SiteId": visit.SiteId,
            "VisitDate": visit.VisitDate,
            "VisitStatus": visit.VisitStatus,
            "SalesPersonId": visit.SalesPersonId,
            "Purpose": visit.Purpose,
            "VisitOutlook": visit.VisitOutlook,
            "CreatedDate": visit.CreatedDate,
            "UpdatedDate": visit.UpdatedDate,
            "CreatedById": visit.CreatedById,
            "site": visit.site,
            "infra": visit.infra,
            "created_by": visit.created_by,
            "VisitorName": visitors_by_visit.get(visit.VisitId, {}).get("VisitorName"),
            "VisitorContactId": visitors_by_visit.get(visit.VisitId, {}).get("ContactId"),
            "VisitorContactType": visitors_by_visit.get(visit.VisitId, {}).get("ContactType"),
            "VisitorContactNo": visitors_by_visit.get(visit.VisitId, {}).get("ContactNo")
        }
        response_data.append(visit_dict)

    return {
        "data": response_data,
        "total_records": total_records,
        "total_pages": total_pages,
        "current_page": sIndex,
        "limit": limit,
        "nextIndex": next_index
    }


@router.get("/Visit_full_details/{visit_id}", status_code=status.HTTP_200_OK )
async def read_visit_full_details_by_id (user:user_dependency, db: db_dependency, visit_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException (status_code=401, detail='Authentication Failed')
    visit_details = db.query(Visit).options(
                     # joinedload(Visit.lead),
                     joinedload(Visit.site).load_only(Site.SiteId, Site.SiteName, Site.SiteAddress),
                     joinedload(Visit.infra).load_only(Infra.InfraId, Infra.InfraName, Infra.InfraCategory),
                     # joinedload(Visit.infraunit),
                     # joinedload(Visit.broker),
                     joinedload(Visit.created_by).load_only(Users.id, Users.FirstName, Users.LastName)
    ).filter(
        Visit.VisitId == visit_id
    ).first()
    if visit_details is not None:
        return visit_details
    raise HTTPException(status_code=404, detail='visit not found')




# @router.get('/visit-summary')
# async def get_visit_summary(
#     user: user_dependency,
#     db: db_dependency,
#     start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
#     end_date: str = Query(..., description="End date in YYYY-MM-DD format")
# ):
#     if user is None:
#         raise HTTPException(status_code=401, detail="Authentication Failed")
#
#     # Parse the dates
#     try:
#         start_dt = datetime.strptime(start_date, "%Y-%m-%d")
#         end_dt = datetime.strptime(end_date, "%Y-%m-%d")
#     except ValueError:
#         raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")
#
#     # Include the full end date day
#     end_dt = end_dt.replace(hour=23, minute=59, second=59)
#
#     # Query total visits
#     total_visits = db.query(func.count(Visit.VisitId)).filter(
#         Visit.VisitDate >= start_dt,
#         Visit.VisitDate <= end_dt
#     ).scalar()
#
#     # Query total direct visits
#     total_direct_visits = db.query(func.count(Visit.VisitId)).filter(
#         Visit.VisitType == 'Direct Visit',
#         Visit.VisitDate >= start_dt,
#         Visit.VisitDate <= end_dt
#     ).scalar()
#
#
#     # Broker visits
#     total_broker_visits = db.query(func.count(Visit.VisitId)).filter(
#         Visit.VisitType == 'Broker Visits',
#         Visit.VisitDate >= start_dt,
#         Visit.VisitDate <= end_dt
#     ).scalar()
#
#     return {
#         "start_date": start_date,
#         "end_date": end_date,
#         "total_visits": total_visits,
#         "total_direct_visits": total_direct_visits,
#         "total_broker_visits": total_broker_visits
#     }



@router.get("/site-wise-count")
async def get_site_wise_visit_count(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    visits = db.query(Visit).options(joinedload(Visit.site)).all()
    site_visit_count = {}
    site_name_map = {}

    for visit in visits:
        if visit.site:
            site_id = visit.site.SiteId
            site_name = visit.site.SiteName

            if site_id in site_visit_count:
                site_visit_count[site_id] += 1
            else:
                site_visit_count[site_id] = 1

            site_name_map[site_id] = site_name  # Safe to overwrite with same value

    # Build result list
    result = []
    for site_id, count in site_visit_count.items():
        result.append({
            "SiteId": site_id,
            "SiteName": site_name_map[site_id],
            "VisitCount": count
        })

    return result



@router.get("/visit_leads/{lead_id}", status_code=status.HTTP_200_OK)
async def visit_leads(user: user_dependency, db: db_dependency, lead_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
        # Step 1: Get VisitIds for the given LeadId
    visit_ids = db.query(Visitors.VisitId).filter(Visitors.LeadId == lead_id).all()
    visit_ids = [v.VisitId for v in visit_ids]

    if not visit_ids:
        return []

    visits = (
        db.query(Visit)
        .options(
            joinedload(Visit.site), # Assuming this is the relationship chain
            joinedload(Visit.infra)
        )
        .filter(Visit.VisitId.in_(visit_ids))
        .all()
    )
    return visits

