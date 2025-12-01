from string import ascii_uppercase

from fastapi import APIRouter, Depends, HTTPException,status
from pytz import timezone
from fastapi import Path
from pydantic import BaseModel,Field
from models import Lead, Contact, ProspectType, Site, Infra, InfraUnit, SiteInfra, Visit
from typing import Annotated
from sqlalchemy.orm import Session,joinedload, load_only
from sqlalchemy import  select, func
from database import SessionLocal
from .auth import get_current_user
from datetime import datetime
from schemas.schemas import InfraRequest


router = APIRouter(
    prefix="/infra",
    tags = ['infra']
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
async def read_infra(user:user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return db.query(Infra).options(joinedload(Infra.site).load_only(Site.SiteName)).all()


@router.get('/getsingleinfra/{infra_id}', status_code=status.HTTP_200_OK)
async def read_infra_by_id (user:user_dependency, db:db_dependency, infra_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    infra_model = db.query(Infra).options(joinedload(Infra.site).load_only(Site.SiteName)).filter(Infra.InfraId == infra_id).first()
    if infra_model is not None:
        return infra_model
    raise HTTPException(status_code=404, detail= 'infra not found')


@router.get('/getinfrabysite/{site_id}', status_code=status.HTTP_200_OK)
async def get_infra_by_site(user: user_dependency, db: db_dependency, site_id: int = Path(gt=0)):
    """
    Get all infra names and IDs for a specific site.
    Returns: List of {InfraId, InfraName} for the given site_id
    """
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    # Verify site exists
    site_exists = db.query(Site).filter(Site.SiteId == site_id).first()
    if not site_exists:
        raise HTTPException(status_code=404, detail='Site not found')

    # Get all infra for this site
    infra_list = db.query(Infra.InfraId, Infra.InfraName).filter(Infra.SiteId == site_id).all()

    # Return formatted response
    return [{"InfraId": infra.InfraId, "InfraName": infra.InfraName} for infra in infra_list]


@router.post('/createinfra', status_code=status.HTTP_201_CREATED)
async def create_infra(user: user_dependency, db:db_dependency, infra_request:InfraRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    new_infra = Infra(**infra_request.dict(), CreatedById=user.get('id'),  CreatedDate=get_time(),  UpdatedDate=get_time())
    db.add(new_infra)
    db.commit()
    db.refresh( new_infra)
    return {"InfraId": new_infra.InfraId}


@router.put("/updateinfra/{infra_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_infra(user: user_dependency, db: db_dependency, infra_id: int, infra_request:InfraRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    infra_exist = db.query(Infra).filter(Infra.InfraId == infra_id).first()
    if infra_exist is None:
        raise HTTPException(status_code=404, detail="infra not found")
    infra_exist.InfraName=infra_request.InfraName
    infra_exist.InfraCategory=infra_request.InfraCategory
    # infra_exist.InfraCategory=infra_request.InfraCategory
    infra_exist.TotalUnits=infra_request.TotalUnits
    infra_exist.AvailableUnits=infra_request.AvailableUnits
    infra_exist.SoldUnits=infra_request.SoldUnits
    infra_exist.BookedUnits=infra_request.BookedUnits
    infra_exist.InfraFloorCount=infra_request.InfraFloorCount
    infra_exist.SiteId=infra_request.SiteId
    infra_exist.UpdatedDate= get_time()
    db.add(infra_exist)
    db.commit()


# @router.delete("/deleteinfra/{infra_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_infra (user: user_dependency, db: db_dependency, infra_id : int =Path(gt=0)):
#     if user is None:
#         raise HTTPException(status_code=401, detail='Authentication Failed')
#     infra_model = db.query(Infra).filter(Infra.InfraId == infra_id).first()
#     if infra_model is None:
#         raise HTTPException(status_code=404, detail="infra not found")
#     db.query(Infra).filter(Infra.InfraId == infra_id).delete()
#     db.commit()


# @router.delete("/deleteinfra/{infra_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_infra(user: user_dependency, db: db_dependency, infra_id: int = Path(gt=0)):
#     if user is None:
#         raise HTTPException(status_code=401, detail="Authentication Failed")
#
#     # Check if Infra exists
#     infra_model = db.query(Infra).filter(Infra.InfraId == infra_id).first()
#     if infra_model is None:
#         raise HTTPException(status_code=404, detail="Infra not found")
#
#     # Check if this InfraId is used in InfraUnit
#     infraunit_exists = db.query(InfraUnit).filter(InfraUnit.InfraId == infra_id).first()
#     if infraunit_exists:
#         raise HTTPException(
#             status_code=400,
#             detail={
#                 "InfraId": infra_id,
#                 "message": "Cannot delete: This InfraId exists in InfraUnit."
#             }
#         )
#
#     # Delete from Infra
#     db.delete(infra_model)
#     db.commit()



@router.delete("/deleteinfra/{infra_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_infra(user: user_dependency, db: db_dependency, infra_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    # Check if Infra exists
    infra_model = db.query(Infra).filter(Infra.InfraId == infra_id).first()
    if infra_model is None:
        raise HTTPException(status_code=404, detail="Infra not found")

    # Check usage in other tables
    dependencies = []

    if db.query(InfraUnit).filter(InfraUnit.InfraId == infra_id).first():
        dependencies.append("InfraUnit")
    if db.query(SiteInfra).filter(SiteInfra.InfraId == infra_id).first():
        dependencies.append("SiteInfra")
    if db.query(Visit).filter(Visit.InfraId == infra_id).first():
        dependencies.append("Visit")
    # Add more checks here as needed (e.g. Reports, Leads, etc.)

    if dependencies:
        raise HTTPException(
            status_code=400,
            detail={
                "InfraId": infra_id,
                "message": f"Cannot delete: InfraId is used in the following table(s): {', '.join(dependencies)}"
            }
        )
    # Delete Infra safely
    db.delete(infra_model)
    db.commit()