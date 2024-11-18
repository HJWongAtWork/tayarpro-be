from fastapi import APIRouter, Depends, Path, HTTPException
from models import Service, User
from database import SessionLocal
from typing_extensions import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from routes.account import get_current_user, Token
from datetime import datetime


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


router = APIRouter()


class ServiceRequest(BaseModel):
    service_id: str = Field(min_length=3, max_length=50)
    typeid: str = Field(min_length=3, max_length=50)
    description: str = Field(min_length=3, max_length=50)
    cartype: str = Field(min_length=3, max_length=50)
    price: float = Field(gt=0)
    status: str = Field(min_length=3, max_length=50)
    createdby: str = Field(min_length=3, max_length=50)


@router.post('/add_service', tags=["Admin Action"])
async def add_service(db: db_dependency, user: user_dependency, service: ServiceRequest):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    check_admin = db.query(User).filter(
        User.accountid == user['accountid'],
        User.isadmin == 'Y'
    ).first()

    if not check_admin:
        raise HTTPException(status_code=401, detail="You are not admin")

    new_service = Service(
        service_id=service.service_id,
        typeid=service.typeid,
        description=service.description,
        cartype=service.cartype,
        price=service.price,
        status=service.status,
        createdby=service.createdby,
        createdat=datetime.now()
    )

    db.add(new_service)
    db.commit()


@router.post('/all_users', tags=["Admin Action"])
async def all_users(db: db_dependency, user: user_dependency):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    check_admin = db.query(User).filter(
        User.accountid == user['accountid']).first()

    if not check_admin:
        raise HTTPException(status_code=401, detail="You are not admin")

    all_users = db.query(User).all()
    return all_users


@router.post('/give_admin_rights', tags=["Admin Action"])
async def give_admin_rights(db: db_dependency, user: user_dependency, accountid: str):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    check_admin = db.query(User).filter(
        User.accountid == user['accountid']).first()

    if not check_admin:
        raise HTTPException(status_code=401, detail="You are not admin")

    user = db.query(User).filter(
        User.accountid == accountid).first()

    user.is_admin = 'Y'
"""
TODO:

1. Add Products (Tyre)
2. Update Service
3. Update Products
4. View All Users
5. Give Admin Rights
6. Dashboard Data
7. View All Transactions
"""
