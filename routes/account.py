from fastapi import APIRouter, Depends, Path, HTTPException
import models
from database import SessionLocal
from typing_extensions import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

router = APIRouter()

#Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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

@router.get("/")
def read_root():
    return {"message": "Welcome to Tyre Brand API"}

# query to retrieve the password by email 
@router.get("/user/{email}")
async def get_customer_password_by_email(email:str, db: Session = Depends(get_db)):
    customer = db.query(models.User).filter(models.User.email == email).first()
    if not customer:
        return {"message": "Customer not found"}
    return {"email": customer.email, "password": customer.password}

@router.get("/user")
async def get_all_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users

# query parameter to authenticate the user
@router.get("/user/")
async def get_customer(email: str, password: str, db: Session = Depends(get_db)):
    customer = db.query(models.User).filter(models.User.email == email, models.User.password == password).first()
    if not customer:
        return {"message": "Customer not FOUND !!"}
    return customer

@router.put("/user/{accountid}")
async def update_user(
    accountid: str,
    user_update: UserUpdate,
    db: Session = Depends(get_db)
):
    db_user = db.query(models.User).filter(models.User.accountid == accountid).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = user_update.dict(exclude_unset=True)
    for key, value in user_data.items():
        setattr(db_user, key, value)

    # Update fullname if firstname or lastname was changed
    if 'firstname' in user_data or 'lastname' in user_data:
        db_user.fullname = f"{db_user.firstname} {db_user.lastname}"

    db.commit()
    db.refresh(db_user)
    return db_user