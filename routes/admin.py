from fastapi import APIRouter, Depends, Path, HTTPException
from models import Service, User, Tyre, Orders
from database import SessionLocal
from typing_extensions import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from routes.account import get_current_user, Token
from datetime import datetime
from typing import Optional
from sqlalchemy import extract, func


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
        Service.serviceid == service.service_id).first()

    if check_service:
        raise HTTPException(
            status_code=400, detail="Service ID already exists")

    new_service = Service(
        serviceid=service.service_id,
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
    itemid: Optional[str] = Field(min_length=3, max_length=50, default=None)
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
    loadindex: int = Field(gt=0)
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


@router.put('/update_tyres', tags=["Admin Action"])
async def update_tyres(db: db_dependency, user: user_dependency, update_tyre: NewTyreRequests):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    check_admin = db.query(User).filter(
        User.accountid == user['accountid']).first()

    if not check_admin:
        raise HTTPException(status_code=401, detail="You are not admin")

    tyre = db.query(Tyre).filter(
        Tyre.itemid == update_tyre.itemid).first()

    if not tyre:
        raise HTTPException(status_code=404, detail="Tyre not found")

    tyre.brandid = update_tyre.brandid
    tyre.description = update_tyre.description
    tyre.cartype = update_tyre.cartype
    tyre.image_link = update_tyre.image_link
    tyre.unitprice = update_tyre.price
    tyre.details = [update_tyre.details1,
                    update_tyre.details2, update_tyre.details3]
    tyre.tyresize = update_tyre.tyresize
    tyre.speedindex = update_tyre.speedindex
    tyre.loadindex = update_tyre.loadindex
    tyre.stockunit = update_tyre.stockunit
    tyre.status = update_tyre.status
    db.commit()

    return tyre


@router.post('/all_users', tags=["Admin Action"])
async def all_users(db: db_dependency, user: user_dependency):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    check_admin = db.query(User).filter(
        User.accountid == user['accountid'],
        User.isAdmin == 'Y'
    ).first()

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

    user.isAdmin = 'Y'

    db.commit()
    db.refresh(user)

    return {
        "message": "Admin rights given",
        "user": user
    }


@router.put('/edit_service', tags=["Admin Action"])
async def edit_service(db: db_dependency, user: user_dependency, service_update: ServiceRequest):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    check_admin = db.query(User).filter(
        User.accountid == user['accountid']).first()

    if not check_admin:
        raise HTTPException(status_code=401, detail="You are not admin")

    service = db.query(Service).filter(
        Service.serviceid == service_update.service_id).first()

    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    service.typeid = service_update.typeid
    service.description = service_update.description
    service.cartype = service_update.cartype
    service.price = service_update.price
    service.status = service_update.status

    db.commit()
    db.refresh(service)


@router.post('/data_dashboard', tags=["Admin Action"])
async def data_dashboard(db: db_dependency, user: user_dependency):

    month_now = datetime.now().month
    year_now = datetime.now().year
    previous_month = month_now - 1

    total_revenue = db.query(func.sum(Orders.totalprice)).filter(
        extract('month', Orders.createdat) == month_now,
        extract('year', Orders.createdat) == year_now
    ).scalar()

    num_orders = db.query(func.count(Orders.orderid)).filter(
        extract('month', Orders.createdat) == month_now,
        extract('year', Orders.createdat) == year_now
    ).scalar()

    this_month_user = db.query(func.count(User.accountid)).filter(
        extract('month', User.createdat) == month_now,
        extract('year', User.createdat) == year_now
    ).scalar()

    if month_now == 1:
        previous_month = 12

        previous_total_revenue = db.query(func.sum(Orders.totalprice)).filter(
            extract('month', Orders.createdat) == previous_month,
            extract('year', Orders.createdat) == year_now - 1
        ).scalar()

        previous_month_users = db.query(func.count(User.accountid)).filter(
            extract('month', User.createdat) == previous_month,
            extract('year', User.createdat) == year_now - 1
        ).scalar()
    else:

        previous_total_revenue = db.query(func.sum(Orders.totalprice)).filter(
            extract('month', Orders.createdat) == previous_month,
            extract('year', Orders.createdat) == year_now
        ).scalar()

        previous_month_users = db.query(func.count(User.accountid)).filter(
            extract('month', User.createdat) == previous_month,
            extract('year', User.createdat) == year_now
        ).scalar()

    return {
        "month_now": month_now,
        "previous_month": previous_month,
        "total_revenue": total_revenue,
        "previous_total_revenue": previous_total_revenue,
        "num_orders": num_orders,
        "this_month_user": this_month_user,
        "previous_month_users": previous_month_users
    }


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
