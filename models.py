# models.py
from sqlalchemy import Column, String, Integer, ForeignKey, Numeric, Text, create_engine, Date, ARRAY
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

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


