from models import Tyre, Service, Car
import pandas as pd
from database import SessionLocal
from models import Car, Products, ServiceType, Brands
from datetime import datetime

product_ids = ["TYRE"]
product_description = ["Tyre"]
service_type_ids = ["ENGOIL", "BRKSVR", "ALGSVR",
                    "ADJSVR", "BLCSVR", "FXWSVR", "OTHSVR"]


service_type_description = ["Engine Oil Service", "Brake Service", "Alignment Service",
                            "Adjustment Service", "Balancing Service", "Fixing Service", "Other Service"]

tyre_brands = ["MICH", "CONT", "BRID", "GODY"]
tyre_description = ["Michelin", "Continental", "Bridgestone", "Goodyear"]


db = SessionLocal()

for idx, product in enumerate(product_ids):
    """
    Insert data into Products Table
    """

    product = Products(productid=product,
                       description=product_description[idx],
                       status="Active",
                       createdat=datetime.now())
    db.add(product)
    db.commit()


for idx, brand in enumerate(tyre_brands):
    """
    Insert data into Brands Table
    """

    brand = Brands(brandid=brand,
                   productid="TYRE",
                   description=tyre_description[idx],
                   status="Active",
                   createdat=datetime.now())
    db.add(brand)
    db.commit()


for idx, service in enumerate(service_type_ids):
    """
    Insert data into ServiceType Table
    """

    service = ServiceType(typeid=service,
                          description=service_type_description[idx],
                          status="Active",
                          createdat=datetime.now())
    db.add(service)
    db.commit()


df = pd.read_csv('data/tyre.csv')
for index, row in df.iterrows():
    """
    Insert Data into Database
    """

    tyre = Tyre(itemid=row['TyreID'],
                productid=row['ProductID'],
                brandid=row['BrandID'],
                description=row['Description'],
                cartype=row['CarType'],
                image_link=row['ImageLink'],
                unitprice=row['UnitPrice'],
                details=[
                    row['Details'],
                    row['Details2'],
                    row['Details3'],
    ],
        tyresize=row['TyreSize'],
        speedindex=row['Speed Index'],
        loadindex=row['Load Index'],
        stockunit=row['StockUnit'],
        status="Active",
        createdat=datetime.now())
    db.add(tyre)
    db.commit()


df = pd.read_csv('data/service.csv')
for index, row in df.iterrows():
    service = Service(
        serviceid=row['serviceid'],
        typeid=row['typeid'],
        description=row['description'],
        cartype=row['cartype'],
        price=row['price'],
        status="Active"
    )

    db.add(service)
    db.commit()


"""
id,brand,model,year,tire_size,carType

"""
df = pd.read_csv('data/car_spec.csv')

for index, row in df.iterrows():
    car = Car(
        car_brand=row['brand'].lower(),
        car_model=row['model'].lower(),
        car_year=row['year'],
        tyre_size=row['tire_size'],
        car_type=row['carType'],

    )

    db.add(car)
    db.commit()
