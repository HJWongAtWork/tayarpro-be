from fastapi import APIRouter, Depends, Path, HTTPException
from fastapi.responses import RedirectResponse
from models import RegisterCar, Car
from database import SessionLocal
from typing import Annotated, Optional
from sqlalchemy.orm import Session
from pydantic import BaseModel, StrictInt, Field
from enum import Enum
from routes.account import get_current_user, Token
from datetime import datetime
from sqlalchemy import and_


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
    Unsure = "Unsure"


class CarRegistrationRequest(BaseModel):
    plate_num: str = Field(min_length=3, max_length=50)
    car_spec_id: StrictInt = Field(gt=0)


class CarRequest(BaseModel):
    plate_number: str = Field(min_length=1, max_length=50)
    car_brand: str = Field(min_length=1, max_length=50)
    car_model: str = Field(min_length=1, max_length=50)
    car_type: str = Field(min_length=1, max_length=50)
    car_year: int = Field(gt=1980)
    tyre_size: Optional[str] = Field(None, min_length=3, max_length=50)


@router.post('/add_new_car', tags=["Cars"], summary="Add new car to the user account")
async def create_car(db: db_dependency, user: user_dependency, car: CarRequest):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    """
    Add Tyre Size Optional to CarRequest
    """

    find_car = db.query(RegisterCar).filter(
        and_(
            RegisterCar.accountid == user['accountid'],
            RegisterCar.platenumber == car.plate_number.lower().replace(" ", ""),
            RegisterCar.isActive == "Y"
        )
    ).first()

    if find_car:
        raise HTTPException(status_code=400, detail="Car already registered")

    else:

        if car.tyre_size.lower() == "unsure" or car.car_type.lower() == "unsure":

            find_car = db.query(Car).filter(
                and_(
                    Car.car_brand == car.car_brand.lower(),
                    Car.car_model == car.car_model.lower(),
                )
            ).first()

            if car.tyre_size.lower() == "unsure":
                car.tyre_size = find_car.tyre_size

            if car.car_type.lower() == "unsure":
                car.car_type = find_car.car_type

        new_car = RegisterCar(
            accountid=user["accountid"],
            platenumber=car.plate_number.lower().replace(" ", ""),
            createdat=datetime.now(),
            carbrand=car.car_brand.lower(),
            carmodel=car.car_model.lower(),
            cartype=car.car_type,
            caryear=car.car_year,
            tyresize=car.tyre_size,)

        db.add(new_car)
        db.commit()
        return {
            "message": "Car successfully registered",
            "carid": new_car.carid
        }


@router.post('/view_car', summary="View all cars registered by user", tags=["Cars"])
async def view_car(db: db_dependency, user: user_dependency):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    car = db.query(RegisterCar).filter(
        and_(
            RegisterCar.accountid == user["accountid"],
            RegisterCar.isActive == "Y"
        )
    ).all()

    return car


class CarStatus(BaseModel):
    car_id: int = Field(gt=0)


@router.post('/change_car_status', summary="Change car status", tags=["Cars"])
async def change_car_status(db: db_dependency, user: user_dependency, car_requests: CarStatus):

    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    car = db.query(RegisterCar).filter(
        and_(
            RegisterCar.accountid == user["accountid"],
            RegisterCar.carid == car_requests.car_id
        )
    ).first()

    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    car.isActive = "N"
    db.add(car)
    db.commit()

    return {
        "message": "Car status successfully changed"
    }


class CarUpdateRequests(BaseModel):
    car_id: int = Field(gt=0)
    car_brand: str = Field(min_length=1, max_length=50)
    car_model: str = Field(min_length=1, max_length=50)
    car_type: CarTypeEnum
    car_year: int = Field(gt=0)
    tyre_size: Optional[str] = Field(None, min_length=1, max_length=50)


@router.put('/update_car', summary="Update car details", tags=["Cars"])
async def update_car(db: db_dependency, user: user_dependency, car_request: CarUpdateRequests):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    car = db.query(RegisterCar).filter(
        and_(
            RegisterCar.accountid == user["accountid"],
            RegisterCar.carid == car_request.car_id
        )
    ).first()

    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    car.carbrand = car_request.car_brand
    car.carmodel = car_request.car_model
    car.caryear = car_request.car_year
    car.tyresize = car_request.tyre_size
    car.cartype = car_request.car_type

    db.add(car)
    db.commit()

    return {
        "message": "Car details successfully updated"
    }


@router.get('/car_brands', summary="Get all car brands", tags=["Cars"])
async def get_car_brands(db: db_dependency):
    car_brands_tuples = db.query(Car.car_brand).distinct().all()
    car_brands = [brand[0] for brand in car_brands_tuples]

    return {
        "car_brands": car_brands
    }


@router.get('/car_models/{car_brand}', summary="Get all car models by brand", tags=["Cars"])
async def get_car_models(db: db_dependency, car_brand: str = Path(...)):
    car_models = db.query(Car.car_model).filter(
        Car.car_brand == car_brand).distinct().all()

    return {
        "car_models": [model[0] for model in car_models]
    }


@router.get('/car_models', summary="Get all car models", tags=["Cars"])
async def get_all_car_models(db: db_dependency):
    car_models = db.query(Car.car_model).distinct().all()
    return {
        "car_models": [model[0] for model in car_models]
    }


@router.get('/tyre_sizes', summary="Get all tyre sizes", tags=["Cars"])
async def get_tyre_sizes(db: db_dependency):
    tyre_sizes = db.query(Car.tyre_size).distinct().all()
    return {
        "tyre_sizes": [size[0] for size in tyre_sizes]
    }


@router.get('/car_years', summary="Get all car years", tags=["Cars"])
async def get_car_years(db: db_dependency):
    car_years = db.query(Car.car_year).distinct().all()
    return {
        "car_years": [year[0] for year in car_years]
    }

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
