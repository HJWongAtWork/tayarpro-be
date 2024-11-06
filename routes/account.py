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
    user = db.query(User).filter(User.username == username).first()
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


class UserUpdate(BaseModel):
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    phonenumber: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zipcode: Optional[str] = None
    gender: Optional[str] = None
    dob: Optional[date] = None


"""
    accountid = Column(String, primary_key=True, index=True)
    firstname = Column(String, index=True)
    lastname = Column(String, index=True)
    phonenumber = Column(String, index=True)
    email = Column(String, index=True)
    address = Column(String, index=True)
    state = Column(String, index=True)
    city = Column(String, index=True)
    zipcode = Column(String, index=True)
    gender = Column(String, index=True)
    fullname = Column(String, index=True)
    password = Column(String, index=True)
    isadmin = Column(String, index=True)
    createdat = Column(DateTime, index=True)
    dob = Column(Date, index=True)
"""


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
    password: str = Field(..., example="123456")


# query to retrieve the password by email
"""Register"""


@router.post("/register", tags=["Authentication"])
async def register_user(user: UserRegisterRequest, db: db_dependency):
    time_now = datetime.now()

    """Check the user is exist or not"""
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(
            status_code=400, detail="Username already registered")

    accountid = str(uuid.uuid4())

    new_user = User(
        accountid=accountid,
        username=user.username,
        firstname=user.firstname,
        lastname=user.lastname,
        phonenumber=user.phonenumber,
        email=user.email,
        address=user.address,
        state=user.state,
        city=user.city,
        zipcode=user.zipcode,
        password=bcrypt_context.hash(user.password),
        createdat=time_now,
        dob=user.dob
    )

    db.add(new_user)
    db.commit()

    return user


class Token(BaseModel):
    access_token: str
    token_type: str


@router.post("/login", response_model=Token, tags=["Authentication"])
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                db: db_dependency):

    user = authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(status_code=401,
                            detail="Could not validate user.")
    else:
        token = create_access_token(
            user.username, user.accountid, timedelta(minutes=60))

        return {"access_token": token, "token_type": "bearer"}


# @router.get("/user/{email}")
# async def get_customer_password_by_email(email: str, db: Session = Depends(get_db)):
#     customer = db.query(User).filter(User.email == email).first()
#     if not customer:
#         return {"message": "Customer not found"}
#     return {"email": customer.email, "password": customer.password}
# @router.get("/user")
# async def get_all_users(db: Session = Depends(get_db)):
#     users = db.query(User).all()
#     return users
# # query parameter to authenticate the user
# @router.get("/user/")
# async def get_customer(email: str, password: str, db: Session = Depends(get_db)):
#     customer = db.query(User).filter(
#         User.email == email, User.password == password).first()
#     if not customer:
#         return {"message": "Customer not FOUND !!"}
#     return customer
# @router.put("/user/{accountid}")
# async def update_user(
#     accountid: str,
#     user_update: UserUpdate,
#     db: Session = Depends(get_db)
# ):
#     db_user = db.query(User).filter(
#         User.accountid == accountid).first()
#     if not db_user:
#         raise HTTPException(status_code=404, detail="User not found")
#     user_data = user_update.dict(exclude_unset=True)
#     for key, value in user_data.items():
#         setattr(db_user, key, value)
#     # Update fullname if firstname or lastname was changed
#     if 'firstname' in user_data or 'lastname' in user_data:
#         db_user.fullname = f"{db_user.firstname} {db_user.lastname}"
#     db.commit()
#     db.refresh(db_user)
#     return db_user
