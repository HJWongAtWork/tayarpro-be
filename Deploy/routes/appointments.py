from fastapi import APIRouter, Depends, Path, HTTPException
from models import Appointment, Orders, OrdersDetail, RegisterCar, Tyre, Service
from database import sessionLocal
from typing_extensions import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from routes.account import get_current_user, Token
import uuid
from datetime import datetime, date, time


# Dependency
def get_db():
    db = sessionLocal()
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

        for detail in order_detail:
            if detail.productid[0] == "T":
                detail.product = db.query(Tyre).filter(
                    Tyre.itemid == detail.productid).first()
            elif detail.productid[0] == "S":
                detail.product = db.query(Service).filter(
                    Service.serviceid == detail.productid).first()

        appointment.order = order
        appointment.order_detail = order_detail

        appointment.car_detail = db.query(RegisterCar).filter(
            RegisterCar.carid == appointment.carid).first()
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
    appointment_bay: int


@router.put('/update_appointment', tags=["Appointments"])
async def update_appointment(appointment_request: AppointmentRequest, user: user_dependency, db: db_dependency):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    check_car_exists = db.query(RegisterCar).filter(
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


@router.post('/get_appointment_details', tags=["Appointments"])
async def get_appointment_details(user: user_dependency, db: db_dependency):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Query for all appointments for the user
    appointments = db.query(Appointment).filter(
        Appointment.accountid == user['accountid']
    ).all()

    if not appointments:
        return {"message": "No appointments found for this user"}

    result = []

    for appointment in appointments:
        # Query for the order associated with each appointment
        order = db.query(Orders).filter(
            Orders.appointmentid == appointment.appointmentid
        ).first()

        if not order:
            result.append({
                "appointment": appointment,
                "order_details": []
            })
            continue

        # Query for the order details, including tyre and service information
        order_details = db.query(
            OrdersDetail,
            RegisterCar,
            Tyre,
            Service
        ).outerjoin(
            RegisterCar, OrdersDetail.carid == RegisterCar.carid
        ).outerjoin(
            Tyre, OrdersDetail.productid == Tyre.itemid
        ).outerjoin(
            Service, OrdersDetail.productid == Service.serviceid
        ).filter(
            OrdersDetail.orderid == order.orderid
        ).all()

        # Process the results
        processed_details = []
        for detail, car, tyre, service in order_details:
            processed_detail = {
                "orderid": detail.orderid,
                "productid": detail.productid,
                "carid": detail.carid,
                "unitprice": float(detail.unitprice),
                "quantity": float(detail.quantity),
                "totalprice": float(detail.totalprice),
                "car": {
                    "carid": car.carid if car else None,
                    "carbrand": car.carbrand if car else None,
                    "carmodel": car.carmodel if car else None,
                    "platenumber": car.platenumber if car else None
                },
                "tyre": {
                    "itemid": tyre.itemid if tyre else None,
                    "description": tyre.description if tyre else None
                },
                "service": {
                    "serviceid": service.serviceid if service else None,
                    "description": service.description if service else None
                }
            }
            processed_details.append(processed_detail)

        result.append({
            "appointment": {
                "appointmentid": appointment.appointmentid,
                "accountid": appointment.accountid,
                "appointmentdate": appointment.appointmentdate,
                "createdat": appointment.createdat,
                "status": appointment.status,
                "appointment_bay": appointment.appointment_bay,
                "carid": appointment.carid
            },
            "order": {
                "orderid": order.orderid,
                "accountid": order.accountid,
                "createdat": order.createdat,
                "totalprice": float(order.totalprice) if order.totalprice else None,
                "appointmentid": order.appointmentid,
                "status": order.status,
                "paymentmethod": order.paymentmethod
            },
            "order_details": processed_details
        })

    return result
