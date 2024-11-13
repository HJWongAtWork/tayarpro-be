from fastapi import APIRouter, Depends, Path, HTTPException
from models import Products, Tyre
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


@router.get("/get_all_tyres", tags=["Products"])
async def get_all_tyres(db: db_dependency):
    tyres = db.query(Tyre).all()
    return tyres

"""
For specific product page in Frontend: -

- To get product details by ID
"""


@router.get('/get_product_by_id/{itemid}', tags=["Products"])
async def get_tyre_by_id(item_id: str, db: db_dependency):
    tyre = db.query(Tyre).filter(Tyre.itemid == item_id).first()
    if not tyre:
        raise HTTPException(status_code=404, detail="Tyre not found")
    return tyre


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


# @router.get("/products")
# def get_products(db: Session = Depends(get_db)):
#     products = db.query(models.Products).all()
#     return products


# @router.get("/brands")
# async def get_brands(db: Session = Depends(get_db)):
#     brands = db.query(models.Brands).all()
#     return brands
