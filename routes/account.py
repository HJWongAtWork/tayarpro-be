from fastapi import APIRouter, Depends, Path, HTTPException
from models import User
from database import SessionLocal
from typing_extensions import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, EmailStr
from datetime import date
from typing import Optional
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import timedelta, datetime, timezone
import uuid


router = APIRouter()

# Dependency


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "4069dd716b31d5c3fd0fc5ffb4823e91223e4ca9dff0159aec1c9ba8bf9b94a1"
ALGORITHM = "HS256"
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="login")


class Token(BaseModel):
    access_token: str
    token_type: str


def authenticate_user(username: str, password: str, db):

    user = db.query(User).filter(User.username ==
                                 username, User.isActive == 'Y').first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.password):
        return False
    return user


def create_access_token(username: str,
                        account_id: int,
                        expires_delta: timedelta):
    encode = {
        "sub": username,
        "accountid": account_id
    }

    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        accountid: int = payload.get("accountid")
        if username is None or accountid is None:
            raise HTTPException(status_code=401,
                                detail="Could not validate user.")

        return {"username": username, "accountid": accountid}
    except JWTError:
        raise HTTPException(status_code=401,
                            detail="Could not validate user.")


class UserRegisterRequest(BaseModel):
    username: str = Field(..., example="rahmanrom")
    firstname: str = Field(..., example="HJ")
    lastname: str = Field(..., example="Wong")
    phonenumber: str = Field(..., example="0123456789")
    email: EmailStr = Field(..., example="rahmanrom@gmail.com")
    address: str = Field(..., example="Jalan 1")
    state: str = Field(..., example="Selangor")
    city: str = Field(..., example="Petaling Jaya")
    zipcode: str = Field(..., example="47810")
    gender: str = Field(..., example="Male")
    password: str = Field(..., example="123456")
    dob: date = Field(..., example="1990-01-01")


class UserRegisterRequestV2(BaseModel):
    email: EmailStr = Field(..., example="rahmanrom@gmail.com")
    password: str = Field(..., example="123456")
    first_name: str = Field(..., example="HJ")
    last_name: str = Field(..., example="Wong")


@router.post("/register-v2", tags=["Authentication"])
async def register_user_v2(user: UserRegisterRequestV2, db: db_dependency):
    """
    Important Point:

    Date is in ISO 8601 Format (Recommended): 1990-12-31 (Year-Month-Day)
    """
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    accountid = str(uuid.uuid4())

    new_user = User(
        accountid=accountid,
        firstname=user.first_name,
        lastname=user.last_name,
        username=user.email,
        email=user.email,
        password=bcrypt_context.hash(user.password),
        createdat=datetime.now())
    db.add(new_user)
    db.commit()

    return {
        "message": "User successfully registered",
        "user_info": new_user.to_dict()  # Use the to_dict method
    }


class Token(BaseModel):
    access_token: str
    token_type: str


@router.post("/login", tags=["Authentication"])
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                db: db_dependency):

    user = authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(status_code=401,
                            detail="Could not validate user.")
    else:
        token = create_access_token(
            user.username, user.accountid, timedelta(minutes=60))

    return {"access_token": token, "token_type": "bearer", "user_info": user.to_dict()}


class UserUpdate(BaseModel):

    firstname: str = Field(..., example="HJ")
    lastname: str = Field(..., example="Wong")
    email: EmailStr = Field(..., example="rahmanrom@gmail.com")
    phone_number: int = Field(..., example="0123456789")


@router.put('/update_user', tags=["User Action"])
async def update_user(
        user_update: UserUpdate,
        db: db_dependency,
        user: Annotated[dict, Depends(get_current_user)]):

    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    check_user = db.query(User).filter(
        User.accountid == user['accountid']).first()

    if not check_user:
        raise HTTPException(status_code=404, detail="User not found")

    if check_user.email == user_update.email:
        check_user.firstname = user_update.firstname
        check_user.lastname = user_update.lastname
        check_user.phonenumber = user_update.phone_number

    else:
        if db.query(User).filter(User.email == user_update.email).first():
            raise HTTPException(
                status_code=400, detail="Email already registered")

        check_user.firstname = user_update.firstname
        check_user.lastname = user_update.lastname
        check_user.email = user_update.email
        check_user.username = user_update.email
        check_user.phonenumber = user_update.phone_number

    db.commit()
    db.refresh(check_user)
    return check_user


@router.put('/update_password', tags=["User Action"])
async def update_password(
        password: str,
        db: db_dependency,
        user: Annotated[dict, Depends(get_current_user)]):
    db_user = db.query(User).filter(
        User.accountid == user['accountid']).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.password = bcrypt_context.hash(password)
    db.commit()
    db.refresh(db_user)
    return db_user


class UsernameRequest(BaseModel):
    username: str


@router.post("/users/username", tags=["User Action"])
async def get_password_by_username(request: UsernameRequest, db: db_dependency):
    username = request.username
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"username": user.username, "password": user.password}


@router.post('/delete_account', tags=["User Action"])
async def delete_account(db: db_dependency, user: Annotated[dict, Depends(get_current_user)]):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    check_user = db.query(User).filter(
        User.accountid == user['accountid']).first()

    if not check_user:
        raise HTTPException(status_code=404, detail="User not found")

    check_user.isActive = "N"
    db.commit()

    return {
        "message": "Account successfully deleted"
    }
