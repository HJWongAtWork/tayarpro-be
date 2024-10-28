from fastapi import APIRouter, Depends, Path, HTTPException
from fastapi.responses import RedirectResponse
from models import Car
from database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel, StrictInt, Field

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class CarRequest(BaseModel):
    car_brand: str = Field(min_length=3, max_length=50)
    car_model: str = Field(min_length=3, max_length=50)
    car_year: StrictInt = Field(gt=1800, lt=2025)
    tyre_size: str = Field(min_length=3, max_length=50)
    car_type: str = Field()  # Can also use Enum for validation


@router.get("/cars")
async def read_all_cars(db: db_dependency):
    return db.query(Car).all()


@router.get("/cars/{car_id}")
async def get_car_by_id(db: db_dependency, car_id: int = Path(gt=0)):
    """
    Read cars by ID
    """
    car_result = db.query(Car).filter(
        Car.carspecID == car_id).first()

    if car_result is not None:
        return car_result
    raise HTTPException(status_code=404, detail="Car Model not found")


@router.post("/cars")
async def create_car(db: db_dependency, car_request: CarRequest):
    new_car = Car(
        car_brand=car_request.car_brand,
        car_model=car_request.car_model,
        car_year=car_request.car_year,
        tyre_size=car_request.tyre_size,
        car_type=car_request.car_type
    )
    db.add(new_car)
    db.commit()
    db.refresh(new_car)
    return new_car


@router.put("/cars/{car_id}")
async def update_car(db: db_dependency,
                     car_id: int,
                     car_request: CarRequest):
    car_result = db.query(Car).filter(
        Car.carspecID == car_id).first()

    if car_result is None:
        raise HTTPException(status_code=404, detail="Car not found")

    car_result.brand = car_request.car_brand
    car_result.model = car_request.car_model
    car_result.year = car_request.car_year
    car_result.tyreSize = car_request.tyre_size
    car_result.carType = car_request.car_type

    db.add(car_result)
    db.commit()
    return {"message": "Car Model successfully updated"}


@router.delete("/cars/{car_id}")
async def delete_car(db: db_dependency, car_id: int = Path(gt=0)):
    car_result = db.query(Car).filter(
        Car.carspecID == car_id).first()

    if car_result is None:
        raise HTTPException(status_code=404, detail="Car not found")
    else:
        db.delete(car_result)
        db.commit()
        return {"message": "Car Model Successfully deleted"}
