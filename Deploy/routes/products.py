from fastapi import APIRouter, Depends, Path, HTTPException, Query
from models import Products, Tyre, Brands, Products, Car, RegisterCar
from database import sessionLocal
from typing_extensions import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from routes.account import get_current_user, Token


def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


router = APIRouter()


"""
For all products page in Frontend
"""


@router.get("/get_all_tyres", summary="Get all of the tyres", tags=["Products"])
async def get_all_tyres(db: db_dependency):

    tyres = db.query(Tyre).order_by(Tyre.createdat.desc()).all()
    return tyres

"""
For specific product page in Frontend: -

- To get product details by ID
"""


@router.get('/get_product_by_id', summary="Get tyre based on the itemid", tags=["Products"])
async def get_tyre_by_id(tyre_id: str, db: db_dependency):
    tyre = db.query(Tyre).filter(Tyre.itemid == tyre_id).first()
    if not tyre:
        raise HTTPException(status_code=404, detail="Tyre not found")
    return tyre


@router.get("/brands", tags=["Products"])
async def get_brands(db: Session = Depends(get_db)):
    brands = db.query(Brands).all()
    return brands


# @router.get("/tyre")
# def get_tyre(db: Session = Depends(get_db)):
#     tyre = db.query(models.Tyre).all()
#     return tyre


# @router.get("/tyre/{itemid}")
# def get_tyre_by_id(itemid: str, db: Session = Depends(get_db)):
#     tyre = db.query(models.Tyre).filter(models.Tyre.itemid == itemid).first()
#     if not tyre:
#         return {"message": "Tyre not found"}
#     return tyre


@router.get("/products", tags=["Products"])
def get_products(db: Session = Depends(get_db)):
    products = db.query(Products).all()
    return products


@router.get('/filter_tyre_by_size', summary="Get Tyre based on Tyre Size", tags=["Tyre"])
async def filter_tyre_by_size(db: Session = Depends(get_db), tyre_size: str = Query(...)):
    tyres = db.query(Tyre).filter(Tyre.tyresize == tyre_size).all()
    return tyres


@router.get('/filter_tyre_by_car_id', summary="Get Tyre based on User Registered Car's ID", tags=["Tyre"])
async def filter_tyre_by_id(db: db_dependency, car_id: str = Query(...)):
    get_car = db.query(RegisterCar).filter(RegisterCar.carid == car_id).first()
    if not get_car:
        raise HTTPException(status_code=404, detail="Car not found")

    tyres = db.query(Tyre).filter(Tyre.tyresize == get_car.tyresize).all()

    return tyres
