from fastapi import APIRouter, Depends, Path, HTTPException
from models import Appointment, Orders, OrdersDetail, RegisterCar
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


@router.post('/all_appointments', tags=["Appointments"])
async def get_all_appointments(db: db_dependency):
    appointments = db.query(Appointment).all()
    return appointments


class AppointmentRequest(BaseModel):
    appointment_id: str
    appointment_date: date
    appointment_time: time
    car_id: int
    appointment_bay: int


@router.put('/update_appointment', tags=["Appointments"])
async def update_appointment(appointment_request: AppointmentRequest, user: user_dependency, db: db_dependency):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    check_car_exists = db.query(RegisterCar).filter(
        RegisterCar.carid == appointment_request.car_id,
        RegisterCar.accountid == user['accountid']).first()

    if not check_car_exists:
        raise HTTPException(status_code=404, detail="Car not found")

    appointment = db.query(Appointment).filter(
        Appointment.appointmentid == appointment_request.appointment_id,
        Appointment.accountid == user['accountid']).first()

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    appointment.appointmentdate = datetime.combine(
        appointment_request.appointment_date, appointment_request.appointment_time)
    appointment.carid = appointment_request.car_id
    appointment.appointment_bay = appointment_request.appointment_bay

    db.add(appointment)
    db.commit()

    return {
        "message": "Appointment successfully updated",
        "appointment": appointment
    }


@router.put('/cancel_appointment', tags=["Appointments"])
async def cancel_appointment(appointment_id: str, user: user_dependency, db: db_dependency):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    appointment = db.query(Appointment).filter(
        Appointment.appointmentid == appointment_id,
        Appointment.accountid == user['accountid']).first()

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    appointment.status = "Cancelled"
    db.commit()

    return {
        "message": "Appointment successfully cancelled"
    }
