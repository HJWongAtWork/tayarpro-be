from fastapi import APIRouter, Depends, Path, HTTPException
import models
from database import SessionLocal
from typing_extensions import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime

router = APIRouter()

#Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def read_root():
    return {"message": "Welcome to Tyre Brand API"}

class CreateOrders(BaseModel):
    orderid:str
    accountid:str
    createdat: datetime = Field(...,format="%Y-%m-%d %H:%M:%S")
    totalprice: Decimal = Field(...,decimal_places=2)
    appointmentid :str

class CreateOrdersDetail(BaseModel):
    orderid:str
    carid:str
    productid:str
    unitprice : Decimal = Field(...,decimal_places=2)
    quantity:int
    totalprice: Decimal = Field(...,decimal_places=2)

class CreateInvoice(BaseModel):
    invoiceid:str
    accountid:str
    methodid:str
    createdat:datetime
    orderid :str
    totalprice:Decimal = Field(...,decimal_places=2)

class CreateAppointment(BaseModel):
    appointmentid :str
    accountid:str
    appointmentday:datetime 
    createdat:datetime = Field(...,format="%Y-%m-%d %H:%M:%S")
    completed:str
    orderid:str


@router.get("/paymentmethod")
def get_paymentmethod(db: Session = Depends(get_db)):
    paymentmethod = db.query(models.PaymentMethod).all()
    return paymentmethod

# get next itemlineno for cart 
@router.get("/orders/next_orderid")
async def get_next_orderid(db: Session = Depends(get_db)):
    try:
        latest_order = db.query(models.Orders).order_by(models.Orders.orderid.desc()).first()
        if latest_order:
            latest_num = int(latest_order.orderid[3:])
            next_num = latest_num + 1
            next_orderid = f"ORD{next_num:04d}"
        else:
            next_orderid = "ORD0001"
        return {"next_orderid": next_orderid}
    except Exception as e:
        return {"error": str(e)}



@router.post("/orders")
async def create_order(order:CreateOrders,db: Session = Depends(get_db)):
    try:
        new_order = models.Orders(
            orderid = order.orderid,
            accountid = order.accountid,
            createdat = order.createdat,
            totalprice = order.totalprice,
            appointmentid = order.appointmentid
        )
        db.add(new_order)
        db.commit()
        db.refresh(new_order)
        return new_order
    except Exception as e:
        return {"error": str(e)}

@router.post("/ordersdetail")
async def create_orderdetail(orderdetail:CreateOrdersDetail,db: Session = Depends(get_db)):
    try:
        new_orderdetail = models.OrdersDetail(
            orderid = orderdetail.orderid,
            carid = orderdetail.carid,
            productid = orderdetail.productid,
            unitprice = orderdetail.unitprice,
            quantity = orderdetail.quantity,
            totalprice = orderdetail.totalprice
        )
        db.add(new_orderdetail)
        db.commit()
        db.refresh(new_orderdetail)
        return new_orderdetail
    except Exception as e:    
        return {"error": str(e)}

@router.get("/invoice/next_invoiceid")
async def get_next_invoiceid(db: Session = Depends(get_db)):
    try:
        latest_invoice = db.query(models.Invoice).order_by(models.Invoice.invoiceid.desc()).first()
        if latest_invoice:
            latest_num = int(latest_invoice.invoiceid[3:])
            next_num = latest_num + 1
            next_invoiceid = f"INV{next_num:04d}"
        else:
            next_invoiceid = "INV0001"
        return {"next_invoiceid": next_invoiceid}
    except Exception as e:    
        return {"error": str(e)}

@router.post("/invoice")
async def create_invoice(invoice:CreateInvoice,db: Session = Depends(get_db)):
    try:
        new_invoice = models.Invoice(
            invoiceid = invoice.invoiceid,
            accountid = invoice.accountid,
            methodid = invoice.methodid,
            createdat = invoice.createdat,
            orderid = invoice.orderid,
            totalprice = invoice.totalprice
        )
        db.add(new_invoice)
        db.commit()
        db.refresh(new_invoice)
        return new_invoice
    except Exception as e:
        return {"error": str(e)}

@router.delete("/cart/{accountid}")
async def delete_cart(accountid: str, db: Session = Depends(get_db)):
    deleted = db.query(models.Cart).filter(models.Cart.accountid == accountid).delete()
    db.commit()
    return {"message": f"{deleted} Cart item(s) deleted"}

@router.post("/appointment")
async def create_appointment(appointment: CreateAppointment, db: Session = Depends(get_db)):
    try:
        new_appointment = models.Appointment(
            appointmentid = appointment.appointmentid,
            accountid = appointment.accountid,
            appointmentday = appointment.appointmentday,
            createdat = appointment.createdat,
            completed = appointment.completed,
            orderid = appointment.orderid
        )
        db.add(new_appointment)
        db.commit()
        db.refresh(new_appointment)
        return new_appointment
    except Exception as e:
        return {"error": str(e)}


@router.get("/appointment")
async def get_appointments(db: Session = Depends(get_db)):
    appointments = db.query(models.Appointment).order_by(models.Appointment.appointmentid).all()
    return appointments

@router.get("/appointment/next_appointmentid")
async def get_next_appointmentid(db: Session = Depends(get_db)):
    try:
        latest_appointment = db.query(models.Appointment).order_by(models.Appointment.appointmentid.desc()).first()
        if latest_appointment:
            latest_num = int(latest_appointment.appointmentid[3:])
            next_num = latest_num + 1
            next_appointmentid = f"APT{next_num:04d}"
        else:
            next_appointmentid = "APT0001"
        return {"next_appointmentid": next_appointmentid}
    except Exception as e:    
        return {"error": str(e)}