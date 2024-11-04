# models.py
from sqlalchemy import Column, String, Integer, ForeignKey, Numeric, Text, create_engine, Date, ARRAY, Enum, DateTime
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import enum
from database import Base, engine



class User(Base):
    __tablename__ = "users"
    accountid = Column(String, primary_key=True, index=True)
    firstname = Column(String, index=True)
    lastname= Column(String, index=True)
    phonenumber = Column(String, index=True)
    email = Column(String, index=True)
    address = Column(String, index=True)
    state = Column(String, index=True)
    city = Column(String, index=True)
    zipcode = Column(String, index=True)
    gender = Column(String, index=True)
    fullname = Column(String, index=True)
    password = Column(String, index=True)
    isadmin = Column(String, index=True)
    createdat = Column(DateTime, index=True)
    dob = Column(Date, index=True)
    
    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"


class CarCategory(enum.Enum):
    SUV = "SUV"
    Passenger = "Passenger"


class Car(Base):
    __tablename__ = "car_specifications"
    # Define the column in the table
    carspecID = Column(Integer, primary_key=True, autoincrement=True)
    car_brand = Column(String, nullable=False)
    car_model = Column(String, nullable=False)
    car_year = Column(Integer, nullable=False)
    tyre_size = Column(String, nullable=False)
    car_type = Column(Enum(CarCategory), nullable=False)

    def __repr__(self):
        return f"Car({self.carspecID}, {self.car_brand}, {self.car_model}, {self.car_year}, {self.tyre_size}, {self.car_type.value})"


class PaymentMethod(Base):
    __tablename__ = "paymentmethod"
    methodid = Column(String, primary_key=True, index=True)
    description = Column(String, index=True)
    status = Column(String, index=True)
    createdat = Column(DateTime, index=True)

class Products(Base):
    __tablename__ = "products"
    productid = Column(String, primary_key=True, index=True)
    description = Column(String, index=True)
    status = Column(String, index=True)
    createdby = Column(String, index=True)
    createdat = Column(DateTime, index=True)

class Brands(Base):
    __tablename__ = "brands"
    brandid = Column(String, primary_key=True, index=True)
    productid = Column(String, index=True)
    description = Column(String, index=True)
    status = Column(String, index=True)
    createdat = Column(DateTime, index=True)
    createdby = Column(String, index=True)
    
class Tyre(Base):   
    __tablename__ = "tyre"
    itemid = Column(String, primary_key=True, index=True)
    productid = Column(String, index=True, nullable=False)
    brandid = Column(String,  index=True,nullable=False)
    description = Column(String, index=True,nullable=False)
    cartype = Column(String, index=True,nullable=False)
    image_link = Column(String, index=True, nullable=False)
    unitprice = Column(Integer,index=True)
    details = Column(String, index=True, nullable=False, server_default='[]')
    tyresize = Column(String, index=True)
    speedindex = Column(String, index=True)
    loadindex = Column(Integer, index=True)
    stockunit = Column(String, index=True)
    status = Column(String, index=True)

class ServiceType(Base):
    __tablename__ = "servicetype"
    typeid = Column(String, primary_key=True, index=True)
    description = Column(String, index=True)
    status = Column(String, index=True)
    createdat = Column(DateTime, index=True)
    createdby = Column(String, index=True)

class Service(Base):
    __tablename__ = "service"
    serviceid = Column(String, primary_key=True, index=True)
    typeid = Column(String, ForeignKey("servicetype.typeid") ,index=True)
    description = Column(String, index=True)
    cartype = Column(String, index=True)
    price = Column(Integer, index=True)
    status = Column(String, index=True)
    createdby = Column(String, index=True)
    createdat = Column(DateTime, index=True)

class Cart(Base):
    __tablename__ = "cart"
    accountid = Column(String, ForeignKey("users.accountid"), index=True, primary_key=True)
    productid = Column(String, primary_key=True,index=True)
    description = Column(String,index=True)
    unitprice = Column(Integer, index=True)
    quantity = Column(Integer, index=True)


class Orders (Base):
    __tablename__ = "orders"
    orderid = Column(String, primary_key=True, index=True)
    accountid = Column(String, ForeignKey("users.accountid"), index=True)
    createdat = Column(DateTime, index=True)
    totalprice = Column(Integer, index=True)
    appointmentid = Column(String, ForeignKey("appointment.appointmentid"), index=True)

class OrdersDetail(Base):
    __tablename__ = "ordersdetail"
    orderid = Column(String, ForeignKey("orders.orderid"),primary_key=True, index=True)
    productid = Column(String, index=True, primary_key=True)
    carid = Column(String, index=True)
    unitprice = Column(Integer, index=True)
    quantity = Column(Integer, index=True)
    totalprice = Column(Integer, index=True)

class Appointment(Base):
    __tablename__ = "appointment"
    appointmentid = Column(String, primary_key=True, index=True)
    accountid = Column(String, ForeignKey("users.accountid"), index=True)
    appointmentday = Column(DateTime, index=True)
    createdat = Column(DateTime, index=True)
    completed = Column(String, index=True)
    orderid = Column(String, index=True)


class Invoice(Base):
    __tablename__ = "invoice"
    invoiceid = Column(String, primary_key=True, index=True)
    accountid = Column(String, index=True)
    methodid = Column(String, index=True)
    createdat = Column(DateTime, index=True)
    orderid = Column(String, index=True)
    totalprice = Column(Integer, index=True)

Base.metadata.create_all(bind=engine)
