from fastapi import APIRouter, Depends, Path, HTTPException
import models
from database import SessionLocal
from typing_extensions import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field


router = APIRouter()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def read_root():
    return {"message": "Welcome to Tyre Brand API"}

@router.get("/service")
def get_service(db:Session = Depends(get_db)):
    service =db.query(models.Service).all()
    return service

@router.get("/servicetype")
def get_servicetype(db:Session = Depends(get_db)):
    servicetype =db.query(models.ServiceType).all()
    return servicetype   

@router.get("/service/{serviceDescription}")
def get_service_by_id(serviceDescription: str, db: Session = Depends(get_db)):
    services = db.query(models.Service).filter(models.Service.description == serviceDescription).all()
    if not services:
        return {"message": "Service not found"}
    return services

@router.get("/service/{serviceDescription}/{cartype}")
def get_service_by_cartype_and_description(serviceDescription: str, cartype: str, db: Session = Depends(get_db)):
    service = db.query(models.Service).filter(models.Service.description == serviceDescription, models.Service.cartype == cartype).all()
    if not service:
        return {"message": "Service not found"}
    return service 