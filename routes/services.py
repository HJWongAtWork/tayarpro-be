from fastapi import APIRouter, Depends, Path, HTTPException
from models import Service, User
from database import SessionLocal
from typing_extensions import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from routes.account import get_current_user, Token


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


router = APIRouter()





@router.get('/get_all_services', summary="List all of the services", tags=["Services"])
async def get_all_services(db: db_dependency):
    services = db.query(Service).all()
    return services


@router.get('/service/',  summary="List service based on the service_id", tags=["Services"])
async def get_service_by_id(service_id: int, db: db_dependency):
    service = db.query(Service).filter(
        Service.service_id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service


@router.get("get_all_service_types", tags=["Services"])
async def get_all_service_types(db: db_dependency):
    services = db.query(Service).all()
    return services


@router.get("service_type/{service_type}", tags=["Services"])
async def get_service_by_type(service_type: str, db: db_dependency):
    service = db.query(Service).filter(
        Service.service_type == service_type).all()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service

    # @router.get("/service")
    # def get_service(db:Session = Depends(get_db)):
    #     service =db.query(models.Service).all()
    #     return service

    # @router.get("/servicetype")
    # def get_servicetype(db:Session = Depends(get_db)):
    #     servicetype =db.query(models.ServiceType).all()
    #     return servicetype

    # @router.get("/service/{serviceDescription}")
    # def get_service_by_id(serviceDescription: str, db: Session = Depends(get_db)):
    #     services = db.query(models.Service).filter(models.Service.description == serviceDescription).all()
    #     if not services:
    #         return {"message": "Service not found"}
    #     return services

    # @router.get("/service/{serviceDescription}/{cartype}")
    # def get_service_by_cartype_and_description(serviceDescription: str, cartype: str, db: Session = Depends(get_db)):
    #     service = db.query(models.Service).filter(models.Service.description == serviceDescription, models.Service.cartype == cartype).all()
    #     if not service:
    #         return {"message": "Service not found"}
    #     return service
