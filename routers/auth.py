from fastapi import APIRouter,Depends
from pydantic import BaseModel, Field, conint
from models import Users
from passlib.context import CryptContext
from database import SessionLocal
from typing import Annotated, Optional, List
from sqlalchemy.orm import Session
from starlette import status
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt , JWTError
from datetime import timedelta, datetime, timezone
from schemas.schemas import RolesRequest

router = APIRouter(
    prefix="/auth",
    tags = ['auth']
)


SECRET_KEY = '281adf67ef0eb8ece714f18bf5086f7e8d632aa23a108d9d653e8cf1d656e87a'
ALGORITHM = 'HS256'

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
db_dependency = Annotated[Session, Depends(get_db)]

bcrypt_context = CryptContext(schemes=['bcrypt'],deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

def authenticate_user(username:str, password:str, db):
    user = db.query (Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password,user.hashedpassword):
        return False
    return user

def create_access_token(username:str, user_id: int, role: str,expires_delta:timedelta):
    encode = {'sub':username,'id':user_id, 'role':role}
    expires = datetime.now(timezone.utc) +expires_delta
    encode.update({'exp':expires})
    return jwt.encode(encode,SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload =jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role: str = payload.get('role')
        if username is None or user_id is None:
            raise HTTPException (status_code=status.HTTP_401_UNAUTHORIZED,detail='Could not validate user')
        return {'username':username,'id':user_id,'user_role':user_role}
    except JWTError:
        raise HTTPException (status_code=status.HTTP_401_UNAUTHORIZED,detail='Could not validate user')


class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name:str
    last_name: str
    password: str
    is_active: bool
    ManagerId: int
    ContactNo: Optional[conint(ge=1000000000, le=9999999999)]
    # RoleAssignments: List[RolesRequest]
    RoleAssignments: List[int]

class Token(BaseModel):
    access_token:str
    token_type:str





@router.post ("/token",response_model=Token,status_code=status.HTTP_200_OK)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm,Depends()],db:db_dependency):
    user = authenticate_user(form_data.username,form_data.password,db)
    if not user:
        raise HTTPException (status_code=status.HTTP_401_UNAUTHORIZED,detail='Could not validate user')
    token = create_access_token(user.username, user.id, user.role,  timedelta(days=3650))
    return {'access_token':token,'token_type':'bearer'}

def verify_token(token: str = Depends(oauth2_bearer)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=403, detail="Token is invalid or expired")
        return payload
    except JWTError:
        
        raise HTTPException(status_code=403, detail="Token is invalid or expired")

@router.get("/verify-token/{token}")
async def verify_user_token(token: str):
    verify_token(token=token)
    return {"message": "Token is valid"}