from fastapi import APIRouter, Depends, HTTPException,status
from pytz import timezone
from fastapi import Path
from pydantic import BaseModel,Field
from models import Lead,Contact, ProspectType, Site, Visit, SiteInfra, AmenitySite
from typing import Annotated
from sqlalchemy.orm import Session,joinedload, load_only
from sqlalchemy import  select, func
from sqlalchemy.exc import IntegrityError
from database import SessionLocal
from .auth import get_current_user
from datetime import datetime
from schemas.schemas import SiteRequest
from routers.security_utils import get_user_site_ids


router = APIRouter(
    prefix="/site",
    tags = ['site']
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


@router.get("/")
async def read_sites(user:user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException (status_code=401, detail='Authentication Failed')
    allowed_site_ids = get_user_site_ids(user, db)
    if not allowed_site_ids:
        raise HTTPException(status_code=403,detail="No site access assigned for this user")
    sites = (db.query(Site).filter(Site.SiteId.in_(allowed_site_ids)).all())
    return sites



@router.get("/getsinglesite/{site_id}", status_code=status.HTTP_200_OK )
async def read_sites (user:user_dependency, db: db_dependency, site_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException (status_code=401, detail='Authentication Failed')
    Site_model = db.query(Site).filter(Site.SiteId==site_id).first()
    if Site_model is not None:
        return Site_model
    raise HTTPException(status_code=404, detail = 'site not found')



@router.post("/createsite",status_code=status.HTTP_201_CREATED)
async def create_site(user: user_dependency, db: db_dependency,site_request:SiteRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    # Check if site name already exists
    existing_site = db.query(Site).filter(Site.SiteName == site_request.SiteName).first()
    if existing_site:
        raise HTTPException(status_code=400, detail=f"Site with name '{site_request.SiteName}' already exists")

    try:
        new_site = Site(**site_request.dict(),CreatedById=user.get('id'), CreatedDate=get_time(), UpdateDate=get_time())
        db.add(new_site)
        db.commit()
        db.refresh( new_site)
        return {"SiteId": new_site.SiteId}
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Site with name '{site_request.SiteName}' already exists")



@router.put("/updatesite/{site_id}", status_code=status.HTTP_204_NO_CONTENT )
async def update_site (user: user_dependency,db: db_dependency,site_id: int, site_request:SiteRequest):
    if user is None:
        raise HTTPException (status_code=401, detail='Authentication Failed')
    existing_site = db.query(Site).filter(Site.SiteId == site_id).first()
    if existing_site is None:
        raise HTTPException (status_code=404, detail="site not found")

    # Check if new site name already exists (excluding current site)
    if site_request.SiteName != existing_site.SiteName:
        duplicate_site = db.query(Site).filter(Site.SiteName == site_request.SiteName, Site.SiteId != site_id).first()
        if duplicate_site:
            raise HTTPException(status_code=400, detail=f"Site with name '{site_request.SiteName}' already exists")

    try:
        existing_site.SiteName = site_request.SiteName
        existing_site.SiteTypeId = site_request.SiteTypeId
        existing_site.SiteCity = site_request.SiteCity
        existing_site.SiteStatus = site_request.SiteStatus
        if site_request.SiteAddress is not None:
            existing_site.SiteAddress = site_request.SiteAddress
        if site_request.SiteSizeSqFt is not None:
            existing_site.SiteSizeSqFt = site_request.SiteSizeSqFt
        if site_request.OperationalDate is not None:
            existing_site.OperationalDate = site_request.OperationalDate
        if site_request.IsOperational is not None:
            existing_site.IsOperational = site_request.IsOperational
        if site_request.DeveloperId is not None:
            existing_site.DeveloperId = site_request.DeveloperId
        if site_request.SiteDescription is not None:
            existing_site.SiteDescription = site_request.SiteDescription
        if site_request.NearbyLandmarks is not None:
            existing_site.NearbyLandmarks = site_request.NearbyLandmarks
        existing_site.UpdateDate = get_time()
        db.add(existing_site)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Site with name '{site_request.SiteName}' already exists")



# @router.delete("/deletesite/{site_id}", status_code=status.HTTP_204_NO_CONTENT )
# async def delete_site (user:user_dependency, db: db_dependency,site_id : int =Path(gt=0)):
#     if user is None:
#         raise HTTPException (status_code=401, detail='Authentication Failed')
#     Site_model = db.query(Site).filter(Site.SiteId==site_id).first()
#     if Site_model is None:
#         raise HTTPException (status_code=404, detail="site not found")
#     db.query(Site).filter(Site.SiteId==site_id).delete()
#     db.commit()


@router.delete("/deletesite/{site_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_site(user: user_dependency, db: db_dependency, site_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    # Check if Site exists
    site_model = db.query(Site).filter(Site.SiteId == site_id).first()
    if site_model is None:
        raise HTTPException(status_code=404, detail="Site not found")

    # Check for references in other tables
    dependencies = []

    if db.query(Visit).filter(Visit.SiteId == site_id).first():
        dependencies.append("Visit")
    if db.query(SiteInfra).filter(SiteInfra.SiteId == site_id).first():
        dependencies.append("SiteInfra")
    if db.query(Lead).filter(Lead.SiteId == site_id).first():
        dependencies.append("Lead")
    if db.query(AmenitySite).filter(AmenitySite.SiteId == site_id).first():
        dependencies.append("AmenitySite")
    # Add more tables if needed

    if dependencies:
        raise HTTPException(
            status_code=400,
            detail={
                "SiteId": site_id,
                "message": f"Cannot delete: SiteId is used in the following table(s): {', '.join(dependencies)}"
            }
        )
    # Delete site safely
    db.delete(site_model)
    db.commit()


@router.patch("/SoftDeleteSite/{site_id}", status_code=status.HTTP_200_OK)
async def soft_delete_site(user: user_dependency, db: db_dependency, site_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    allowed_site_ids = get_user_site_ids(user, db)
    if not allowed_site_ids:
        raise HTTPException(status_code=403, detail="No site access assigned for this user")

    site_model = db.query(Site).filter(Site.SiteId == site_id, Site.SiteId.in_(allowed_site_ids)).first()
    if site_model is None:
        raise HTTPException(status_code=404, detail="Site not found")

    if site_model.IsDeleted == 1:
        raise HTTPException(status_code=400, detail="Site is already deleted")

    site_model.IsDeleted = 1
    site_model.UpdateDate = get_time()
    db.commit()

    return {
        "message": "Site soft deleted successfully",
        "SiteId": site_id,
        "statusCode": 200
    }


@router.get("/site-full-details")
async def site_full_details(user:user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException (status_code=401, detail='Authentication Failed')
    sites = db.query(Site).options(
        joinedload(Site.sitetype),
              joinedload(Site.developer),
              joinedload(Site.created_by)
    ).all()
    return sites














