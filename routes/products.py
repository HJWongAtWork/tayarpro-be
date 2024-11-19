from fastapi import APIRouter, Depends, Path, HTTPException
from models import Products, Tyre, Brands, Products
from database import SessionLocal
from typing_extensions import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from routes.account import get_current_user, Token


def get_db():
    db = SessionLocal()
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
    tyres = db.query(Tyre).all()
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
