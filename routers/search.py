from sqlalchemy import or_
from fastapi import Depends, APIRouter, HTTPException, Query
# from models import Lead, Contact, ProspectType, Site
from sqlalchemy.orm import Session, joinedload
from starlette import status

from database import SessionLocal
from models import Lead, Contact, Site
from .auth import get_current_user
from typing import Annotated, Dict, Any

router = APIRouter(
    prefix="/UniversalSearch",
    tags = ['universal Search']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


# @router.get('/search/')
# async def search(user: user_dependency,db: db_dependency,query: str = Query(...)):
#     if user is None:
#         raise HTTPException(status_code=401, detail="Authentication Failed")
#     results = []
#     leads = db.query(Lead).filter(Lead.LeadName.ilike(f"%{query}%")).all()
#     results.extend([{"type": "lead", "data": lead} for lead in leads])
#     contacts = db.query(Contact).filter(
#         or_(
#             Contact.ContactFName.ilike(f"%{query}%"),
#             Contact.ContactNo.ilike(f"%{query}%")
#         )
#     ).all()
#     results.extend([{"type": "contact", "data": contact} for contact in contacts])
#     sites = db.query(Site).filter(Site.SiteName.ilike(f"%{query}%")).all()
#     results.extend([{"type": "site", "data": site} for site in sites])
#     print("Search Results:", results)
#     if len (results) == 0:
#         raise HTTPException(status_code=404, detail="Search not found")
#     return {"results": results}


# -------------------------------------------------------------------------------------------------------------------


@router.get('/')
async def universal_search(user: user_dependency, db: db_dependency, query: str = Query(...)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    leads = (
        db.query(Lead, Contact, Site)
        .join(Contact, Lead.ContactId == Contact.ContactId, isouter=True)
        .join(Site, Lead.SiteId == Site.SiteId, isouter=True)
        .filter(
            or_(
                Lead.LeadName.ilike(f"%{query}%"),  # Search by LeadName
                Lead.LeadType.ilike(f"%{query}%"),  # Search by LeadType
                Lead.LeadSource.ilike(f"%{query}%"),  # Search by LeadSource
                Lead.CreatedDate.ilike(f"%{query}%"),  # Search by LeadCreateDate

                Contact.ContactFName.ilike(f"%{query}%"),  # Search by Contact FName
                Contact.ContactLName.ilike(f"%{query}%"),  # Search by Contact LName
                Contact.ContactEmail.ilike(f"%{query}%"),  # Search by Contact Email
                Contact.ContactNo.ilike(f"%{query}%"),  # Search by Contact Number
                Contact.ContactType.ilike(f"%{query}%"),  # Search by Contact Type

                Site.SiteName.ilike(f"%{query}%")  # Search by Site Name
            )
        )
        .all()
    )
    results = []
    for lead, contact, site in leads:
        if lead:
            results.append({
                "type": "lead",
                "data": {
                    "LeadId": lead.LeadId,
                    "LeadName": lead.LeadName,
                    "LeadType": lead.LeadType,
                    "LeadSource": lead.LeadSource,
                    "LeadCreatedDate": lead.CreatedDate

                }
            })
        if contact:
            results.append({
                "type": "contact",
                "data": {
                    "ContactId": contact.ContactId,
                    "ContactFName": contact.ContactFName,
                    "ContactLName": contact.ContactLName,
                    "ContactEmail": contact.ContactEmail,
                    "ContactNo": contact.ContactNo,
                    "ContactType": contact.ContactType


                }
            })
        if site:
            results.append({
                "type": "site",
                "data": {
                    "SiteId": site.SiteId,
                    "SiteName": site.SiteName
                }
            })
    # if not results:
        # raise HTTPException(status_code=404, detail="Search not found")
    return results


# --------------------------------------------------------------------------------------------------------------------

# @router.get('/search/')
# async def search(user: user_dependency, db: db_dependency, query: str = Query(...)):
#     if user is None:
#         raise HTTPException(status_code=401, detail="Authentication Failed")
#     lead_results = []
#     contact_results = []
#     site_results = []
#     leads = (
#         db.query(Lead, Contact, Site)
#         .join(Contact, Lead.LeadContactId == Contact.ContactId, isouter=True)
#         .join(Site, Lead.InterestedSiteId == Site.Siteid, isouter=True)
#         .filter(Lead.LeadName.ilike(f"%{query}%"))  # Search by LeadName
#         .all()
#     )
#     for lead, _, _ in leads:
#         lead_results.append({
#             "type": "lead",
#             "data": {
#                 "LeadName": lead.LeadName
#             }
#         })
#     contacts = (
#         db.query(Contact)
#         .filter(
#             or_(
#                 Contact.ContactFName.ilike(f"%{query}%"),  # Search by Contact Name
#                 Contact.ContactNo.ilike(f"%{query}%")  # Search by Contact Number
#             )
#         )
#         .all()
#     )
#     for contact in contacts:
#         contact_results.append({
#             "type": "contact",
#             "data": {
#                 "ContactFName": contact.ContactFName,
#                 "ContactNo": contact.ContactNo
#             }
#         })
#     sites = (
#         db.query(Site)
#         .filter(Site.SiteName.ilike(f"%{query}%"))  # Search by Site Name
#         .all()
#     )
#     for site in sites:
#         site_results.append({
#             "type": "site",
#             "data": {
#                 "SiteName": site.SiteName
#             }
#         })
#     if lead_results:
#         return lead_results
#     elif contact_results:
#         return contact_results
#     elif site_results:
#         return site_results
#     else:
#         raise HTTPException(status_code=404, detail="No matching results found")

























