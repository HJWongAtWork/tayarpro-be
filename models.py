# models.py
from sqlalchemy import Column, String, Integer, ForeignKey, Numeric, Text, create_engine, Date, ARRAY ,Enum
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import enum
from database import Base

Base = declarative_base()


class Users(Base):
    __tablename__ = 'user'
    # How to make the email unique

    user_id = Column(Integer, primary_key=True)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)  # hashed password
    username = Column(String(255), nullable=False, unique=True)
    gender = Column(String(255), nullable=False)
    created_at = Column(Date, nullable=False)
    is_admin = Column(Integer, nullable=False, default=0)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    address = Column(String(255), nullable=False)
    city = Column(String(255), nullable=False)
    state = Column(String(255), nullable=False)
    zip_code = Column(Integer, nullable=False)

    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"
    
class CarCategory(enum.Enum):
    SUV = "SUV"
    Passenger = "Passenger"
    

class Car(Base):
    __tablename__ = "car_specifications"
    #Define the column in the table
    carspecID = Column(Integer, primary_key=True , autoincrement=True)
    car_brand = Column (String,nullable=False)
    car_model = Column (String,nullable=False)
    car_year = Column (Integer,nullable=False)
    tyre_size = Column (String,nullable=False)
    car_type = Column (Enum(CarCategory), nullable=False)

def __repr__(self):
    return f"Car({self.carspecID}, {self.car_brand}, {self.car_model}, {self.car_year}, {self.tyre_size}, {self.car_type.value})"


