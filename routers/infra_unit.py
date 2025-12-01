from operator import and_
from string import ascii_uppercase

from fastapi import APIRouter, Depends, HTTPException,status, Query
from pytz import timezone
from fastapi import Path
from pydantic import BaseModel,Field
from models import Lead, Contact, ProspectType, Site, InfraUnit, SiteInfra, Infra
from typing import Annotated, Optional, List
from sqlalchemy.orm import Session,joinedload, load_only
from sqlalchemy import select, func, text
from database import SessionLocal
from .auth import get_current_user
from datetime import datetime
from schemas.schemas import InfraUnitRequest
from sqlalchemy import or_


router = APIRouter(
    prefix="/infra_unit",
    tags = ['infra_unit']
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
async def read_infra_unit(user:user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return db.query(InfraUnit).all()




@router.get('/getsingleinfraunit/{infra_unit_id}', status_code=status.HTTP_200_OK)
async def read_infra_unit_by_id (user:user_dependency, db:db_dependency, infra_unit_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    infra_unit_model = db.query(InfraUnit).filter(InfraUnit.InfraUnitId == infra_unit_id).first()
    if infra_unit_model is not None:
        return infra_unit_model
    raise HTTPException(status_code=404, detail= 'infra unit not found')





# @router.post('/create-InfraUnit', status_code=status.HTTP_201_CREATED)
# async def create_infra_unit(user: user_dependency, db:db_dependency, infraunit_request:List[InfraUnitRequest]):
#     if user is None:
#         raise HTTPException(status_code=401, detail='Authentication Failed')
#     new_infra_units = []
#     for request in infraunit_request:
#         unit = InfraUnit(**request.dict(), CreatedById=user.get('id'), CreatedDate=get_time(), UpdateDate=get_time())
#         db.add( unit)
#         new_infra_units.append(unit)
#     db.commit()
#     for unit in new_infra_units:
#         db.refresh(unit)
#     return {"InfraUnitIds":  [unit.InfraUnitId for unit in new_infra_units]}



# @router.post('/create-InfraUnit', status_code=status.HTTP_201_CREATED)
# async def create_infra_unit(user: user_dependency, db: db_dependency, infraunit_request: List[InfraUnitRequest]):
#     if user is None:
#         raise HTTPException(status_code=401, detail='Authentication Failed')
#     # Prepare list of dicts for bulk insert
#     infraunit_data = [{**request.dict(), "CreatedById": user.get('id'), "CreatedDate": get_time(), "UpdateDate": get_time()}
#         for request in infraunit_request
#     ]
#     # Bulk insert in one DB call
#     db.bulk_insert_mappings(InfraUnit, infraunit_data)
#     db.commit()
#     return {"message": f"{len(infraunit_data)} InfraUnits created successfully"}



# @router.post('/create-InfraUnit', status_code=status.HTTP_201_CREATED)
# async def create_infra_unit(user: user_dependency, db: db_dependency, infraunit_request: List[InfraUnitRequest]):
#     if user is None:
#         raise HTTPException(status_code=401, detail='Authentication Failed')
#     infraunit_objects = [InfraUnit(**request.dict(),CreatedById=user.get('id'),CreatedDate=get_time(),UpdateDate=get_time())
#         for request in infraunit_request
#     ]
#     db.add_all(infraunit_objects)
#     db.commit()
#     db.refresh(infraunit_objects[0])  # refresh first one (optional, all will have IDs now)
#
#     created_ids = [obj.InfraUnitId for obj in infraunit_objects]
#
#     return {
#         "message": f"{len(created_ids)} InfraUnits created successfully",
#         "ids": created_ids
#     }



@router.post('/create-InfraUnit', status_code=status.HTTP_201_CREATED)
async def create_infra_unit(user: user_dependency,db: db_dependency,infraunit_request: List[InfraUnitRequest]):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    infraunit_objects = [InfraUnit(**request.dict(),CreatedById=user.get("id"),CreatedDate=get_time(),UpdateDate=get_time())
        for request in infraunit_request
    ]
    db.add_all(infraunit_objects)
    db.commit()

    # refresh to get InfraUnitId values
    for obj in infraunit_objects:
        db.refresh(obj)

    created_infraunit_ids = [obj.InfraUnitId for obj in infraunit_objects]

    # Step 2: Auto create SiteInfra for each InfraUnit
    siteinfra_objects = []
    for infraunit in infraunit_objects:
        # get SiteId from Infra table using InfraId
        infra_record = db.query(Infra).filter(Infra.InfraId == infraunit.InfraId).first()
        if not infra_record:
            raise HTTPException(status_code=404, detail=f"InfraId {infraunit.InfraId} not found")

        siteinfra_objects.append(
            SiteInfra(
                SiteId=infra_record.SiteId,
                InfraId=infraunit.InfraId,
                InfraUnitId=infraunit.InfraUnitId,
                InfraType=infraunit.InfraType,   # use value from InfraUnit
                Active=infraunit.Active,         # use value from InfraUnit
                CreatedDate=get_time(),
                UpdatedDate=get_time(),
                CreatedById=user.get("id")
            )
        )

    if siteinfra_objects:
        db.add_all(siteinfra_objects)
        db.commit()
        for obj in siteinfra_objects:
            db.refresh(obj)
        created_siteinfra_ids = [obj.SiteInfraId for obj in siteinfra_objects]
    else:
        created_siteinfra_ids = []

    return {
        "message": f"{len(created_infraunit_ids)} InfraUnits and {len(created_siteinfra_ids)} SiteInfra records created successfully",
        "infraunit_ids": created_infraunit_ids,
        "siteinfra_ids": created_siteinfra_ids
    }





















@router.put("/updateinfraunit/{infra_unit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_infra_unit(user: user_dependency, db: db_dependency, infra_unit_id: int, infraunit_request:InfraUnitRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    infra_unit_exist = db.query(InfraUnit).filter(InfraUnit.InfraUnitId == infra_unit_id).first()
    if infra_unit_exist is None:
        raise HTTPException(status_code=404, detail="infra unit not found")
    infra_unit_exist.InfraId = infraunit_request.InfraId
    infra_unit_exist.UnitNumber = infraunit_request.UnitNumber
    infra_unit_exist.FloorNumber = infraunit_request.FloorNumber
    infra_unit_exist.UnitSize = infraunit_request.UnitSize
    infra_unit_exist.AvailabilityStatus = infraunit_request.AvailabilityStatus
    infra_unit_exist.Direction = infraunit_request.Direction
    infra_unit_exist.UnitType = infraunit_request.UnitType
    infra_unit_exist.View = infraunit_request.View
    infra_unit_exist.PurchaseReason = infraunit_request.PurchaseReason
    # infra_unit_exist.CreatedDate = infraunit_request.CreatedDate
    infra_unit_exist.UpdateDate = get_time()
    # infra_unit_exist.CreatedById = infraunit_request.CreatedById
    db.add(infra_unit_exist)
    db.commit()





@router.delete("/deleteinfraunit/{infra_unit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_infra_unit (user: user_dependency, db: db_dependency, infra_unit_id : int =Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    infra_unit_model = db.query(InfraUnit).filter(InfraUnit.InfraUnitId == infra_unit_id).first()
    if infra_unit_model is None:
        raise HTTPException(status_code=404, detail="infra unit not found")
    db.query(InfraUnit).filter(InfraUnit.InfraUnitId == infra_unit_id).delete()
    db.commit()






@router.get('/option_search')
async def search(
    user: user_dependency,
    db: db_dependency,
    query: Optional[str] = Query(None, title="General Search"),
    floor_number: Optional[int] = Query(None, title="Floor Number"),
    direction: Optional[str] = Query(None, title="Direction"),
    unit_type: Optional[str] = Query(None, title="Unit Type"),
    view: Optional[str] = Query(None, title="View"),
    site_id: Optional[int] = Query(None, title="Site ID")
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    # query_set = db.query(InfraUnit)
    # filters = []

    if site_id is not None:
        query_set = db.query(InfraUnit).outerjoin(SiteInfra,
        and_( InfraUnit.InfraId == SiteInfra.InfraId, InfraUnit.InfraUnitId == SiteInfra.InfraUnitId)) \
            .filter(SiteInfra.SiteId == site_id)
    else:
        query_set = db.query(InfraUnit)

    filters = []

    if query:
        try:
            query_as_int = int(query)
            filters.append(or_(
                InfraUnit.FloorNumber == query_as_int,
                InfraUnit.UnitNumber == query_as_int
            ))
        except ValueError:
            try:
                query_as_float = float(query)
                filters.append(InfraUnit.UnitSize == query_as_float)
            except ValueError:
                filters.append(or_(
                    InfraUnit.AvailabilityStatus.ilike(f"%{query}%"),
                    InfraUnit.Direction.ilike(f"%{query}%"),
                    InfraUnit.UnitType.ilike(f"%{query}%"),
                    InfraUnit.View.ilike(f"%{query}%")
                ))

    if floor_number is not None:
        filters.append(InfraUnit.FloorNumber == floor_number)
    if direction:
        filters.append(InfraUnit.Direction.ilike(f"%{direction}%"))
    if unit_type:
        filters.append(InfraUnit.UnitType.ilike(f"%{unit_type}%"))
    if view:
        filters.append(InfraUnit.View.ilike(f"%{view}%"))

    # if site_id is not None:
    #     filters.append(InfraUnit.SiteId == site_id)

    if filters:
        query_set = query_set.filter(*filters)

    infra_units = query_set.all()

    results = [
        {
            "type": "infra_unit",
            "data": {
                "FloorNumber": unit.FloorNumber,
                "UnitNumber": unit.UnitNumber,
                "UnitSize": unit.UnitSize,
                "AvailabilityStatus": unit.AvailabilityStatus,
                "Direction": unit.Direction,
                "UnitType": unit.UnitType,
                "View": unit.View,
                "InfraUnitId": unit.InfraUnitId
            }
        }
        for unit in infra_units
    ]

    # if not results:
    #     raise HTTPException(status_code=404, detail="No matching records found")
    return results




@router.get('/search')
async def search(
    user: user_dependency,
    db: db_dependency,
    query: Optional[str] = Query(None, title="General Search"),
    floor_number: Optional[int] = Query(None, title="Floor Number"),
    direction: Optional[str] = Query(None, title="Direction"),
    unit_type: Optional[str] = Query(None, title="Unit Type"),
    view: Optional[str] = Query(None, title="View"),
    site_id: Optional[int] = Query(None, title="Site ID")
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    # query_set = db.query(InfraUnit)
    # filters = []

    if site_id is not None:
        query_set = db.query(InfraUnit).outerjoin(SiteInfra,
        and_( InfraUnit.InfraId == SiteInfra.InfraId, InfraUnit.InfraUnitId == SiteInfra.InfraUnitId)) \
            .filter(SiteInfra.SiteId == site_id)
    else:
        query_set = db.query(InfraUnit)

    filters = []

    if query:
        try:
            query_as_int = int(query)
            filters.append(or_(
                InfraUnit.FloorNumber == query_as_int,
                InfraUnit.UnitNumber == query_as_int
            ))
        except ValueError:
            try:
                query_as_float = float(query)
                filters.append(InfraUnit.UnitSize == query_as_float)
            except ValueError:
                filters.append(or_(
                    InfraUnit.AvailabilityStatus.ilike(f"%{query}%"),
                    InfraUnit.Direction.ilike(f"%{query}%"),
                    InfraUnit.UnitType.ilike(f"%{query}%"),
                    InfraUnit.View.ilike(f"%{query}%")
                ))

    if floor_number is not None:
        filters.append(InfraUnit.FloorNumber == floor_number)
    if direction:
        filters.append(InfraUnit.Direction.ilike(f"%{direction}%"))
    if unit_type:
        filters.append(InfraUnit.UnitType.ilike(f"%{unit_type}%"))
    if view:
        filters.append(InfraUnit.View.ilike(f"%{view}%"))

    # if site_id is not None:
    #     filters.append(InfraUnit.SiteId == site_id)

    if filters:
        query_set = query_set.filter(*filters)

    infra_units = query_set.all()

    results = [
        {
                "FloorNumber": unit.FloorNumber,
                "UnitNumber": unit.UnitNumber,
                "UnitSize": unit.UnitSize,
                "AvailabilityStatus": unit.AvailabilityStatus,
                "Direction": unit.Direction,
                "UnitType": unit.UnitType,
                "View": unit.View,
                "InfraUnitId": unit.InfraUnitId,
                "InfraId": unit.InfraId
        }
        for unit in infra_units
    ]

    # if not results:
    #     raise HTTPException(status_code=404, detail="No matching records found")
    return results
