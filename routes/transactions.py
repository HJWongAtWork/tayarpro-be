from fastapi import APIRouter, Depends, Path, HTTPException
from models import Cart, Tyre, Service, Orders, OrdersDetail, Appointment, Invoice
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


"""
Add Service to Cart
"""


class addServiceToCart(BaseModel):
    service_id: str
    quantity: int = Field(..., gt=0,
                          description="Quantity must be greater than 0")


class addTyreToCart(BaseModel):
    tyre_id: str
    quantity: int = Field(..., gt=0,
                          description="Quantity must be greater than 0")


@router.post('/add_service_to_cart', tags=["Cart"])
async def add_service_to_cart(db: db_dependency, user: user_dependency, service: addServiceToCart):
    """
    service_id: int
    quantity: int


    If not user: Unauthorized
    Check Cart:
    If ServiceID exists, increment quantity
    Else, add new service to Cart

    """

    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Find the Service ID in Cart

    check_services = db.query(Service).filter(
        Service.serviceid == service.service_id).first()

    if not check_services:
        raise HTTPException(status_code=404, detail="Service not found")

    check_cart = db.query(Cart).filter(
        Cart.accountid == user['accountid'], Cart.productid == service.service_id).first()

    if check_cart:
        check_cart.quantity += service.quantity
        db.commit()
        return {"message": "Service added to Cart"}

    else:
        new_cart = Cart(
            accountid=user['accountid'],
            productid=service.service_id,
            quantity=service.quantity,
            unitprice=check_services.price,
            description=check_services.description
        )

        db.add(new_cart)
        db.commit()

        all_carts = db.query(Cart).filter(
            Cart.accountid == user['accountid']).all()
        return {"message": "Service added to Cart", "carts": all_carts}


@router.post('/add_tyre_to_cart', tags=["Cart"])
async def add_tyre_to_cart(db: db_dependency, user: user_dependency, tyre: addTyreToCart):
    """
    tyre_id: int
    quantity: int

    If not user: Unauthorized
    Check Cart:
    If TyreID exists, increment quantity
    Else, add new tyre to Cart
    """

    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Find the Tyre ID in Cart

    check_tyres = db.query(Tyre).filter(
        Tyre.itemid == tyre.tyre_id).first()

    if not check_tyres:
        raise HTTPException(status_code=404, detail="Tyre not found")

    check_cart = db.query(Cart).filter(
        Cart.accountid == user['accountid'], Cart.productid == tyre.tyre_id).first()

    if check_cart:
        check_cart.quantity += tyre.quantity
        db.commit()

    else:
        new_cart = Cart(
            accountid=user['accountid'],
            productid=tyre.tyre_id,
            quantity=tyre.quantity,
            unitprice=check_tyres.unitprice,
            description=check_tyres.description
        )

        db.add(new_cart)
        db.commit()

    all_carts = db.query(Cart).filter(
        Cart.accountid == user['accountid']).all()

    return {
        "message": "Tyre added to Cart",
        "carts": all_carts
    }


@router.post('/get_cart', tags=['Cart'])
async def cart_using_post(db: db_dependency, user: user_dependency):
    """
    Cart data using post method
    """
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    cart = db.query(Cart).filter(Cart.accountid == user['accountid']).all()

    return cart

"""
=======================
Checkout, Invoicing and Appointments
=======================
"""


class CheckoutCarts(BaseModel):
    """
    Appointment Date: YYYY-MM-DD
    Appointment Time:   HH:MM
    Appointment Bay:   1, 2, 3, 4, 5
    Car ID: 
    """
    car_id: str = Field(..., description="Car ID")
    appointment_date: date = Field(default=date(
        2023, 1, 24), description="Appointment Date")
    appointment_time: time = Field(default=time(
        14, 30), description="Appointment Time")
    appointment_bay: int = Field(..., description="Appointment Bay")


@router.post('/checkout', tags=['Checkout'], summary="Checkout the cart")
async def checkout(db: db_dependency, user: user_dependency, checkout: CheckoutCarts):
    """
    Pre-check:
    1. Check if a user is logged in
    2. Check if the cart is empty

    ----

    1. Create Order
    2. Copy all of the item in carts to OrderDetail
    3. Create Appointment
    4. Link the Appointment ID to Order
    """
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    all_carts = db.query(Cart).filter(
        Cart.accountid == user['accountid']).all()

    if not all_carts:
        raise HTTPException(status_code=400, detail="Cart is empty")

    order_id = str(uuid.uuid4())
    total_price = 0

    for cart in all_carts:
        total_price = total_price + (cart.unitprice * cart.quantity)

    new_order = Orders(
        orderid=order_id,
        accountid=user['accountid'],
        totalprice=total_price,
        createdat=datetime.now(),
    )

    db.add(new_order)
    db.commit()

    for cart in all_carts:
        new_order_detail = OrdersDetail(
            orderid=order_id,
            productid=cart.productid,
            quantity=cart.quantity,
            unitprice=cart.unitprice,
            carid=checkout.car_id,
            totalprice=(cart.unitprice * cart.quantity)
        )

        db.add(new_order_detail)
        db.commit()

    # Empty the cart
    db.query(Cart).filter(Cart.accountid == user['accountid']).delete()
    db.commit()

    new_appointment = Appointment(
        appointmentid=str(uuid.uuid4()),
        accountid=user['accountid'],
        appointmentdate=datetime.combine(
            checkout.appointment_date, checkout.appointment_time),
        createdat=datetime.now(),
        status="Pending",
        appointment_bay=checkout.appointment_bay
    )

    db.add(new_appointment)
    db.commit()

    return {
        "message": "Checkout successful",
        "order_id": order_id,
    }


@router.post('/get_all_orders', tags=['Orders'])
async def get_all_orders(db: db_dependency, user: user_dependency):
    """
    Get all orders
    """
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    all_orders = db.query(Orders).filter(
        Orders.accountid == user['accountid']).all()

    return all_orders


@router.post('/get_order_detail', tags=['Orders'])
async def get_order_detail(db: db_dependency, user: user_dependency, order_id: str):
    """
    Get order detail by order_id
    """
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    order_detail = db.query(OrdersDetail).filter(
        OrdersDetail.orderid == order_id).all()

    order = db.query(Orders).filter(Orders.orderid == order_id).first()

    if not order_detail:
        raise HTTPException(status_code=404, detail="Order not found")

    return {
        "order": order,
        "order_detail": order_detail
    }
