from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
from google.cloud.sql.connector import Connector

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
# DB_HOST = os.getenv("DB_HOST")
# DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
INSTANCE_CONNECTION_NAME = os.getenv(
    "INSTANCE_CONNECTION_NAME", "connection_name")


def getconn():
    connector = Connector()
    conn = connector.connect(INSTANCE_CONNECTION_NAME,
                             "pg8000", user=DB_USER, password=DB_PASSWORD, db=DB_NAME)
    return conn


engine = create_engine(
    "postgresql+pg8000://", creator=getconn)

sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
# engine = create_engine(SQLALCHEMY_DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()
