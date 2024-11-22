from fastapi import APIRouter, Depends, Path, HTTPException
from models import Appointment, Orders, OrdersDetail
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


@router.post('/get_appointment', tags=["Appointments"])
async def get_appointment(user: user_dependency, db: db_dependency):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    appointments = db.query(Appointment).filter(
        Appointment.accountid == user['accountid']).all()

    for appointment in appointments:
        order = db.query(Orders).filter(
            Orders.appointmentid == appointment.appointmentid).first()

        order_detail = db.query(OrdersDetail).filter(
            OrdersDetail.orderid == order.orderid).all()

        appointment.order = order
        appointment.order_detail = order_detail

    return appointments


@router.post('/get_appointment/{appointment_id}', tags=["Appointments"])
async def get_appointment_by_id(appointment_id: str, user: user_dependency, db: db_dependency):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    appointment = db.query(Appointment).filter(
        Appointment.appointmentid == appointment_id,
        Appointment.accountid == user['accountid']).first()

    order = db.query(Orders).filter(
        Orders.appointmentid == appointment_id).first()

    order_detail = db.query(OrdersDetail).filter(
        OrdersDetail.orderid == order.orderid).all()

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    return {
        "appointment": appointment,
        "order": order,
        "order_detail": order_detail
    }


class AppointmentRequest(BaseModel):
    appointment_date: date
    appointment_time: time
    service_id: str
    car_id: str
