from fastapi import APIRouter, Depends, Path, HTTPException
from fastapi.responses import RedirectResponse
# from models import Car, CarCategory,CarRegistration
from database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel, StrictInt, Field
from enum import Enum
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


class CarTypeEnum(str, Enum):
    SUV = "SUV"
    Passenger = "Passenger"


class CarRegistrationRequest(BaseModel):
    plate_num: str = Field(min_length=3, max_length=50)
    car_spec_id: StrictInt = Field(gt=0)


class CarRequest(BaseModel):
    car_brand: str = Field(min_length=3, max_length=50)
    car_model: str = Field(min_length=3, max_length=50)
    car_year: StrictInt = Field(gt=1800, lt=2025)
    tyre_size: str = Field(min_length=3, max_length=50)
    car_type: CarTypeEnum


"""Need to have data at Car Specification"""


@router.post('/add_new_car')
async def create_car(db: db_dependency, user: user_dependency, car: CarRegistrationRequest):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    new_car = CarRegistration(
        plate_num=car.plate_num,
        car_spec_id=car.car_spec_id,
        accountid=user["accountid"],
        added_at=datetime.now()

    )

    db.add(new_car)
    db.commit()
    return {
        "message": "Car successfully registered",
        "carid": new_car.carid
    }


"""
View cars registered owned by the user
"""


@router.post('/view_car')
async def view_car(db: db_dependency, user: user_dependency):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    car = db.query(CarRegistration).filter(
        CarRegistration.accountid == user["accountid"]).all()
    return car


# # Define the Enum for Car Type


# class CarResponse(BaseModel):
#     carspecID: int
#     car_brand: str
#     car_model: str
#     car_year: int
#     tyre_size: str
#     car_type: CarTypeEnum

#     class Config:
#         orm_mode = True

# # Helper function to retrieve a car or raise 404
# def get_car_or_404(db: Session, car_id: int):
#     car = db.query(Car).filter(Car.carspecID == car_id).first()
#     if car is None:
#         raise HTTPException(status_code=404, detail="Car not found")
#     return car


# @router.get("/cars")
# async def read_all_cars(db: db_dependency):
#     return db.query(Car).all()


# @router.get("/cars/{car_id}")
# async def get_car_by_id(db: db_dependency, car_id: int = Path(gt=0)):
#     """
#     Read cars by ID
#     """
#     return get_car_or_404(db, car_id)


# @router.post("/cars")
# async def create_car(db: db_dependency, car_request: CarRequest):
#     new_car = Car(
#         car_brand=car_request.car_brand,
#         car_model=car_request.car_model,
#         car_year=car_request.car_year,
#         tyre_size=car_request.tyre_size,
#         car_type=car_request.car_type
#     )
#     db.add(new_car)
#     db.commit()
#     db.refresh(new_car)
#     return new_car


# @router.put("/cars/{car_id}")
# async def update_car(db: db_dependency,
#                      car_id: int,
#                      car_request: CarRequest):
#     car_result = get_car_or_404(db, car_id)

#     car_result.car_brand = car_request.car_brand
#     car_result.car_model = car_request.car_model
#     car_result.car_year = car_request.car_year
#     car_result.tyre_size = car_request.tyre_size
#     car_result.car_type = car_request.car_type

#     db.add(car_result)
#     db.commit()
#     return {"message": "Car Model successfully updated"}


# @router.delete("/cars/{car_id}")
# async def delete_car(db: db_dependency, car_id: int = Path(gt=0)):
#     car_result = get_car_or_404(db, car_id)
#     db.delete(car_result)
#     db.commit()
#     return {"message": "Car Model Successfully deleted"}
