from fastapi import APIRouter, Depends, HTTPException,status
from pytz import timezone
from fastapi import Path
from pydantic import BaseModel,Field
from models import SiteInfra, Infra, Site
from typing import Annotated
from sqlalchemy.orm import Session,joinedload, load_only
from sqlalchemy import  select, func
from database import SessionLocal
from .auth import get_current_user
from datetime import datetime
from schemas.schemas import SiteInfraRequest


router = APIRouter(
    prefix="/site_infra",
    tags = ['site_infra']
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
async def read_site_infra(user:user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return db.query(SiteInfra).all()




@router.get('/getsinglesiteinfra/{site_infra_id}', status_code=status.HTTP_200_OK)
async def read_site_infra_by_id (user:user_dependency, db:db_dependency, site_infra_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    site_infra_model = db.query(SiteInfra).filter(SiteInfra.SiteInfraId == site_infra_id).first()
    if site_infra_model is not None:
        return site_infra_model
    raise HTTPException(status_code=404, detail= 'site detail not found')





@router.post('/createsiteinfra', status_code=status.HTTP_201_CREATED)
async def create_site_infra(user: user_dependency, db:db_dependency, siteinfra_request:SiteInfraRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    new_site_infra = SiteInfra(
        SiteId=siteinfra_request.SiteId,
        InfraId=siteinfra_request.InfraId,
        InfraUnitId=siteinfra_request.InfraUnitId,
        InfraType=siteinfra_request.InfraType,
        Active=siteinfra_request.Active,
        CreatedDate=siteinfra_request.CreatedDate,
        UpdatedDate=siteinfra_request.UpdatedDate,
        CreatedById=siteinfra_request.CreatedById
    )
    db.add(new_site_infra)
    db.commit()
    if new_site_infra is not  None:
        return new_site_infra
    raise HTTPException(status_code=404, detail='site detail not found')





@router.put("/updatesiteinfra/{site_infra_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_site_infra(user: user_dependency, db: db_dependency, site_infra_id: int, siteinfra_request:SiteInfraRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    site_infra_exist = db.query(SiteInfra).filter(SiteInfra.SiteInfraId == site_infra_id ).first()
    if site_infra_exist is None:
        raise HTTPException(status_code=404, detail="site detail not found")
    site_infra_exist.SiteId=siteinfra_request.SiteId
    site_infra_exist.InfraId=siteinfra_request.InfraId
    site_infra_exist.InfraUnitId=siteinfra_request.InfraUnitId
    site_infra_exist.InfraType=siteinfra_request.InfraType
    site_infra_exist.Active=siteinfra_request.Active
    site_infra_exist.CreatedDate=siteinfra_request.CreatedDate
    site_infra_exist.UpdatedDate=siteinfra_request.UpdatedDate
    site_infra_exist.CreatedById=siteinfra_request.CreatedById
    db.add(site_infra_exist)
    db.commit()





@router.delete("/deletesiteinfra/{site_infra_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_site_infra (user: user_dependency, db: db_dependency, site_infra_id : int =Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    site_infra_model = db.query(SiteInfra).filter(SiteInfra.SiteInfraId == site_infra_id).first()
    if site_infra_model is None:
        raise HTTPException(status_code=404, detail="site detail not found")
    db.query(SiteInfra).filter(SiteInfra.SiteInfraId == site_infra_id).delete()
    db.commit()




@router.get("/siteinfra/{site_id}", status_code=status.HTTP_200_OK )
async def get_infra_by_site (user:user_dependency, db: db_dependency,site_id : int =Path(gt=0)):
    if user is None:
        raise HTTPException (status_code=401, detail='Authentication Failed')
    result = db.query(
        Infra.InfraName,
        Infra.InfraId,
        Infra.InfraCategory,
        Infra.TotalUnits,
        Infra.AvailableUnits,
        Infra.SoldUnits,
        Infra.BookedUnits,
        Infra.InfraFloorCount,
        Infra.CreatedDate,
        Infra.UpdatedDate,
        Infra.CreatedById,
        Site.SiteName,
        SiteInfra.SiteId
    ).join(
        SiteInfra, SiteInfra.InfraId == Infra.InfraId
    ).join(
        Site, Site.SiteId == SiteInfra.SiteId
    ).filter(
        SiteInfra.SiteId == site_id
    ).all()

    if not result:
        raise HTTPException(status_code=400, detail="No infrastructure found for this SiteId")
    # return [
    #     {
    #         "InfraName": infra.InfraName,
    #         "InfraId": infra.InfraId,
    #         "InfraCategory": infra.InfraCategory,
    #         "TotalUnits": infra.TotalUnits,
    #         "AvailableUnits": infra.AvailableUnits,
    #         "SoldUnits": infra.SoldUnits,
    #         "BookedUnits": infra.BookedUnits,
    #         "InfraFloorCount": infra.InfraFloorCount,
    #         "CreatedDate": infra.CreatedDate,
    #         "UpdatedDate": infra.UpdatedDate,
    #         "CreatedById": infra.CreatedById,
    #         "SiteName": infra.SiteName,
    #         "SiteId": infra.SiteId
    #     }
    #     for infra in result
    # ]

    seen_ids = set()
    unique_data = []

    for infra in result:
        if infra.InfraId not in seen_ids:
            seen_ids.add(infra.InfraId)
            unique_data.append({
                "InfraName": infra.InfraName,
                "InfraId": infra.InfraId,
                "InfraCategory": infra.InfraCategory,
                "TotalUnits": infra.TotalUnits,
                "AvailableUnits": infra.AvailableUnits,
                "SoldUnits": infra.SoldUnits,
                "BookedUnits": infra.BookedUnits,
                "InfraFloorCount": infra.InfraFloorCount,
                "CreatedDate": infra.CreatedDate,
                "UpdatedDate": infra.UpdatedDate,
                "CreatedById": infra.CreatedById,
                "SiteName": infra.SiteName,
                "SiteId": infra.SiteId
            })

    return unique_data


