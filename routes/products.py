from fastapi import APIRouter, Depends, Path, HTTPException
import models
from database import SessionLocal
from typing_extensions import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field


router = APIRouter()

#Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def read_root():
    return {"message": "Welcome to Tyre Brand API"}

@router.get("/tyre")
def get_tyre(db: Session = Depends(get_db)):
    tyre = db.query(models.Tyre).all()
    return tyre

@router.get("/tyre/{itemid}")
def get_tyre_by_id(itemid: str, db: Session = Depends(get_db)):
    tyre = db.query(models.Tyre).filter(models.Tyre.itemid == itemid).first()
    if not tyre:
        return {"message": "Tyre not found"}
    return tyre

@router.get("/products")
def get_products(db:Session = Depends(get_db)):
    products =db.query(models.Products).all()
    return products

@router.get("/brands")
async def get_brands(db: Session = Depends(get_db)):
    brands = db.query(models.Brands).all()
    return brands