from fastapi import APIRouter, Depends, HTTPException,status
from fastapi import Path
from pydantic import BaseModel,Field
from models import Todos
from typing import Annotated 
from sqlalchemy.orm import Session
from database import SessionLocal
from .auth import get_current_user

router = APIRouter(
    prefix="/todos",
    tags = ['todo']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

class TodoRequest(BaseModel):
    Title: str= Field(min_length=3)
    Description: str = Field(min_length=3,max_length=100)
    Priority: int =Field(gt=0,lt=6)
    Complete: bool

@router.get("/")
async def read_all (user:user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException (status_code=401, detail='Authentication Failed')
    return db.query(Todos).all()


@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK )
async def read_todo (user:user_dependency, db: db_dependency,todo_id :int=Path(gt=0)):
    if user is None:
        raise HTTPException (status_code=401, detail='Authentication Failed')
    todo_model = db.query(Todos).filter(Todos.TodosId==todo_id).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail = 'Todo not found')


@router.post("/todo/create_todo", status_code=status.HTTP_201_CREATED )
async def create_todo (user: user_dependency, db: db_dependency,
                       todo_request:TodoRequest):
     if user is None:
         raise HTTPException (status_code=401, detail='Authentication Failed')
     todo_model = Todos(**todo_request.dict(),UserId = user.get('id'))
     db.add(todo_model)
     db.commit()


@router.put("/todo/{todoid}", status_code=status.HTTP_204_NO_CONTENT )
async def update_todo (user: user_dependency,db: db_dependency,todoid: int ,todo_request:TodoRequest):
    if user is None:
        raise HTTPException (status_code=401, detail='Authentication Failed')
    todo_model = db.query(Todos).filter(Todos.TodosId==todoid).filter(Todos.UserId== user.get('id') ).first()
    if todo_model is None:
        raise HTTPException (status_code=404, detail="Todo not found")
    todo_model.Title = todo_request.Title
    todo_model.Description = todo_request.Description
    todo_model.Complete = todo_request.Complete
    todo_model.Priority = todo_request.Priority
    db.add(todo_model)
    db.commit()


@router.delete("/todo/{todoid}", status_code=status.HTTP_204_NO_CONTENT )
async def delete_todo (user:user_dependency, db: db_dependency,todoid: int =Path(gt=0)):
    if user is None:
        raise HTTPException (status_code=401, detail='Authentication Failed')
    todo_model = db.query(Todos).filter(Todos.TodosId==todoid).filter(Todos.UserId == user.get('id')).first()
    if todo_model is None:
        raise HTTPException (status_code=404, detail="Todo not found")
    db.query(Todos).filter(Todos.TodosId==todoid).delete()
    db.commit()