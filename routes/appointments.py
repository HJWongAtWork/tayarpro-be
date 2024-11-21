from fastapi import APIRouter, Depends, Path, HTTPException
from models import Appointment
from database import SessionLocal
from typing_extensions import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from routes.account import get_current_user, Token
import uuid
from datetime import datetime, date, time


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


class AppointmentRequest(BaseModel):
    appointment_id: str = Field(min_length=3, max_length=50)


@router.post('/get_appointment', tags=["Appointments"], summary="Get appointment based on the appointment_id")
async def get_appointment(user: user_dependency, db: db_dependency):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    check_appointment = db.query(Appointment).filter(
        Appointment.accountid == user['accountid'])

    if not check_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    return check_appointment
