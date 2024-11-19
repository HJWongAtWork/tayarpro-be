from fastapi import APIRouter, Depends, Path, HTTPException
from models import Service, User, Tyre
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

    check_service = db.query(Service).filter(
        Service.service_id == service.service_id).first()

    if check_service:
        raise HTTPException(
            status_code=400, detail="Service ID already exists")

    new_service = Service(
        service_id=service.service_id,
        typeid=service.typeid,
        description=service.description,
        cartype=service.cartype,
        price=service.price,
        status=service.status,
        createdby=user['accountid'],
        createdat=datetime.now()
    )

    db.add(new_service)
    db.commit()


class NewTyreRequests(BaseModel):
    itemid: str = Field(min_length=3, max_length=50)
    brandid:  str = Field(min_length=3, max_length=50)
    description: str = Field(min_length=3, max_length=50)
    cartype: str = Field(min_length=3, max_length=50)
    image_link: str = Field(min_length=3, max_length=50)
    price: float = Field(gt=0)
    details1: str = Field(min_length=3, max_length=50)
    details2: str = Field(min_length=3, max_length=50)
    details3: str = Field(min_length=3, max_length=50)
    tyresize: str = Field(min_length=3, max_length=50)
    speedindex: str = Field(min_length=3, max_length=50)
    loadindex: str = Field(min_length=3, max_length=50)
    stockunit: int = Field(gt=0)
    status: str = Field(min_length=3, max_length=50)


@router.post('/add_tyres', tags=["Admin Action"])
async def admin_add_products(db: db_dependency, user: user_dependency, tyre: NewTyreRequests):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    check_admin = db.query(User).filter(
        User.accountid == user['accountid']).first()

    if not check_admin:
        raise HTTPException(status_code=401, detail="You are not admin")

    new_tyre = Tyre(
        itemid=tyre.itemid,
        productid="TYRE",
        brandid=tyre.brandid,
        description=tyre.description,
        cartype=tyre.cartype,
        image_link=tyre.image_link,
        unitprice=tyre.price,
        details=[tyre.details1, tyre.details2, tyre.details3],
        tyresize=tyre.tyresize,
        speedindex=tyre.speedindex,
        loadindex=tyre.loadindex,
        stockunit=tyre.stockunit,
        status=tyre.status,
        createdat=datetime.now(),
        createdby=user['accountid']
    )

    db.add(new_tyre)
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
    db.commit()


class ServiceUpdateRequest(BaseModel):
    typeid: str = Field(min_length=3, max_length=50)
    description: str = Field(min_length=3, max_length=50)
    cartype: str = Field(min_length=3, max_length=50)
    price: float = Field(gt=0)
    status: str = Field(min_length=3, max_length=50)


@router.put('/edit_service', tags=["Admin Action"])
async def edit_service(db: db_dependency, user: user_dependency, service: ServiceRequest):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    check_admin = db.query(User).filter(
        User.accountid == user['accountid']).first()

    if not check_admin:
        raise HTTPException(status_code=401, detail="You are not admin")

    service = db.query(Service).filter(
        Service.service_id == service.service_id).first()

    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    service.typeid = service.typeid
    service.description = service.description
    service.cartype = service.cartype
    service.price = service.price
    service.status = service.status
    db.commit()


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
