# from string import ascii_uppercase
#
# from fastapi import APIRouter, Depends, HTTPException,status
# from pytz import timezone
# from fastapi import Path
# from pydantic import BaseModel,Field
# from models import Lead, Contact, ProspectType, Site, Broker
# from typing import Annotated
# from sqlalchemy.orm import Session,joinedload, load_only
# from sqlalchemy import  select, func
# from database import SessionLocal
# from .auth import get_current_user
# from datetime import datetime
# from schemas.schemas import BrokerRequest
#
#
# router = APIRouter(
#     prefix="/broker",
#     tags = ['broker']
# )
#
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
#
#
# def get_time():
#     ind_time = datetime.now(timezone("Asia/Kolkata"))
#     return ind_time
#
# db_dependency = Annotated[Session, Depends(get_db)]
# user_dependency = Annotated[dict, Depends(get_current_user)]
#
#
# @router.get('/')
# async def read_broker(user:user_dependency, db: db_dependency):
#     if user is None:
#         raise HTTPException(status_code=401, detail="Authentication Failed")
#     return db.query(Broker).all()
#
#
#
#
# @router.get('/getsinglebroker/{broker_id}', status_code=status.HTTP_200_OK)
# async def read_broker_by_id (user:user_dependency, db:db_dependency, broker_id: int = Path(gt=0)):
#     if user is None:
#         raise HTTPException(status_code=401, detail='Authentication Failed')
#     broker_model = db.query(Broker).filter(Broker.Brokerid == broker_id).first()
#     if broker_model is not None:
#         return broker_model
#     raise HTTPException(status_code=404, detail= 'broker not found')
#
#
#
#
#
# @router.post('/createbroker', status_code=status.HTTP_201_CREATED)
# async def create_broker(user: user_dependency, db:db_dependency, broker_request:BrokerRequest):
#     if user is None:
#         raise HTTPException(status_code=401, detail='Authentication Failed')
#     new_broker = Broker(
#         BrokerFirstName=broker_request.BrokerFirstName,
#         BrokerLastName=broker_request.BrokerLastName,
#         BrokerEmail=broker_request.BrokerEmail,
#         BrokerCity=broker_request.BrokerCity,
#         BrokerAddress=broker_request.BrokerAddress,
#         BrokerType=broker_request.BrokerType,
#         is_active=broker_request.is_active
#     )
#     db.add(new_broker)
#     db.commit()
#     if new_broker is not  None:
#         return new_broker
#     raise HTTPException(status_code=404, detail='broker not found')
#
#
#
#
#
# @router.put("/updatebroker/{broker_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def update_broker(user: user_dependency, db: db_dependency, broker_id: int, broker_request:BrokerRequest):
#     if user is None:
#         raise HTTPException(status_code=401, detail='Authentication Failed')
#     broker_exist = db.query(Broker).filter(Broker.Brokerid == broker_id).first()
#     if broker_exist is None:
#         raise HTTPException(status_code=404, detail="broker not found")
#     broker_exist.BrokerFirstName=broker_request.BrokerFirstName
#     broker_exist.BrokerLastName=broker_request.BrokerLastName
#     broker_exist.BrokerEmail=broker_request.BrokerEmail
#     broker_exist.BrokerCity=broker_request.BrokerCity
#     broker_exist.BrokerAddress=broker_request.BrokerAddress
#     broker_exist.BrokerType=broker_request.BrokerType
#     broker_exist.is_active=broker_request.is_active
#     db.add(broker_exist)
#     db.commit()
#
#
#
#
#
# @router.delete("/deletebroker/{broker_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_broker (user: user_dependency, db: db_dependency, broker_id : int =Path(gt=0)):
#     if user is None:
#         raise HTTPException(status_code=401, detail='Authentication Failed')
#     broker_model = db.query(Broker).filter(Broker.Brokerid == broker_id).first()
#     if broker_model is None:
#         raise HTTPException(status_code=404, detail="broker not found")
#     db.query(Broker).filter(Broker.Brokerid == broker_id).delete()
#     db.commit()

