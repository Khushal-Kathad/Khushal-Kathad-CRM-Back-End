from fastapi import APIRouter, Depends, HTTPException,status
from pytz import timezone
from fastapi import Path
from pydantic import BaseModel,Field
from models import FileTracker
from typing import Annotated
from sqlalchemy.orm import Session,joinedload, load_only
from sqlalchemy import  select, func
from database import SessionLocal
from .auth import get_current_user
from datetime import datetime
from schemas.schemas import LeavesRequest


router = APIRouter(
    prefix="/FileTracker",
    tags = ['FileTracker']
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
async def read_Files(user:user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return db.query(FileTracker).all()


@router.get('/get-single-file/{file_id}', status_code=status.HTTP_200_OK)
async def read_files_id (user:user_dependency, db:db_dependency, file_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    file_model = db.query(FileTracker).filter(FileTracker.FileId == file_id).first()
    if file_model is not None:
        return file_model
    raise HTTPException(status_code=404, detail= 'file not found')