from fastapi import APIRouter, Depends, HTTPException,status
from pytz import timezone
from fastapi import Path
from pydantic import BaseModel,Field
from models import Account
from typing import Annotated
from sqlalchemy.orm import Session,joinedload, load_only
from sqlalchemy import  select, func
from database import SessionLocal
from .auth import get_current_user
from datetime import datetime
from schemas.schemas import AccountRequest


router = APIRouter(
    prefix="/Account",
    tags = ['Account']
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
async def read_account(user:user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return db.query(Account).all()


@router.get('/getsingleaccount/{account_id}', status_code=status.HTTP_200_OK)
async def read_account_by_id (user:user_dependency, db:db_dependency, account_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    account_model = db.query(Account).filter(Account.AccountId == account_id).first()
    if account_model is not None:
        return account_model
    raise HTTPException(status_code=404, detail= 'account not found')


@router.post('/createaccount', status_code=status.HTTP_201_CREATED)
async def create_account(user: user_dependency, db:db_dependency, account_request:AccountRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    account = Account(
        AccountName=account_request.AccountName,
        Industry=account_request.Industry,
        Website=account_request.Website,
        Phone=account_request.Phone,
        Address=account_request.Address,
        AccountOwnerId=account_request.AccountOwnerId,
        CreatedDate=account_request.CreatedDate,
        UpdatedDate=account_request.UpdatedDate,
        CreatedById=account_request.CreatedById
    )
    db.add(account)
    db.commit()
    if account_request is not None:
        return account_request
    raise HTTPException(status_code=404, detail='account not found')


@router.put("/updateaccount/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_account(user: user_dependency, db: db_dependency, account_id: int, account_request:AccountRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    account_exist = db.query(Account).filter(Account.AccountId == account_id ).first()
    if account_exist is None:
        raise HTTPException(status_code=404, detail="account detail not found")
    account_exist.AccountName=account_request.AccountName
    account_exist.Industry=account_request.Industry
    account_exist.Website=account_request.Website
    account_exist.Phone=account_request.Phone
    account_exist.Address=account_request.Address
    account_exist.AccountOwnerId=account_request.AccountOwnerId
    account_exist.CreatedDate=account_request.CreatedDate
    account_exist.UpdatedDate=account_request.UpdatedDate
    account_exist.CreatedById=account_request.CreatedById
    db.add(account_exist)
    db.commit()


@router.delete("/deleteaccount/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account (user: user_dependency, db: db_dependency, account_id : int =Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    account_model = db.query(Account).filter(Account.AccountId == account_id).first()
    if account_model is None:
        raise HTTPException(status_code=404, detail="account detail not found")
    db.query(Account).filter(Account.AccountId == account_id).delete()
    db.commit()