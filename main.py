from fastapi import FastAPI, HTTPException, Depends, Header, Path
from database import engine, SessionLocal
import models
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import routes.auth as auth
import routes.products as products
import routes.services as services
from pydantic import BaseModel, StrictInt, Field
from sqlalchemy.orm import Session
from typing import Annotated

app = FastAPI(title="TayarPro API",
              description="API for TayarPro", version="1.0.0")


# Allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # This allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # This allows all HTTP methods
    allow_headers=["*"],  # This allows all headers
)


Base.metadata.create_all(bind=engine)

"""
Compile the Routing Files Together
"""
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(services.router)


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)

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
    car_type: str = Field() # Can also use Enum for validation

#To read all cars:
@app.get("/cars")
async def read_all(db: db_dependency):
    return db.query(models.Car).all()

@app.get("/cars/{car_id}")
async def get_car_by_id(db: db_dependency, car_id: int = Path(gt=0)):
    car_result = db.query(models.Car).filter(models.Car.carspecID == car_id).first()

    if car_result is not None:
        return car_result

    raise HTTPException(status_code=404, detail="Car Model not found")

#To create new Car Spec Repo:
@app.post("/cars")
async def create_car(db: db_dependency, car_request: CarRequest):
    new_car = models.Car( 
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

#Endpoint to update car data:
@app.put("/cars/{car_id}")
async def update_book(db: db_dependency,
                      car_id: int,
                      car_request: CarRequest):
    car_result = db.query(models.Car).filter(models.Car.carspecID == car_id).first()

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

#Endpoint to delete car data:
@app.delete("/cars/{car_id}")
async def delete_book(db: db_dependency, car_id: int = Path(gt=0)):
    car_result = db.query(models.Car).filter(models.Car.carspecID == car_id).first()

    if car_result is None:
        raise HTTPException(status_code=404, detail="Car not found")
    else:
        db.delete(car_result)
        db.commit()
        return {"message": "Car Model Successfully deleted"}