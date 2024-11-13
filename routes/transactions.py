from fastapi import APIRouter, Depends, Path, HTTPException
from models import Cart, Tyre, Service
from database import SessionLocal
from typing_extensions import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from routes.account import get_current_user, Token


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
    quantity: int


class addTyreToCart(BaseModel):
    tyre_id: str
    quantity: int


@router.post('/add_service_to_cart', tags=["Transactions"])
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
        return {"message": "Service added to Cart"}


@router.post('/add_tyre_to_cart', tags=["Transactions"])
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
        return {"message": "Tyre added to Cart"}

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
        return {"message": "Tyre added to Cart"}


@router.get('/get_cart', tags=["Transactions"])
async def get_cart(db: db_dependency, user: user_dependency):
    """
    Get Cart for the user
    """

    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    cart = db.query(Cart).filter(Cart.accountid == user['accountid']).order_by(Cart.productid).all()

    return cart

@router.delete('/remove_from_cart/{product_id}', tags=["Transactions"])
async def remove_from_cart(product_id: str, db: db_dependency, user: user_dependency):
    """
    Remove item from cart
    """
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Find the cart item
    cart_item = db.query(Cart).filter(
        Cart.accountid == user['accountid'],
        Cart.productid == product_id
    ).first()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Item not found in cart")

    # Delete the item
    db.delete(cart_item)
    db.commit()
    return {"message": "Item removed from cart"}

@router.put('/update_cart_quantity/{product_id}/{quantity}', tags=["Transactions"])
async def update_cart_quantity(
    product_id: str,
    quantity: int,
    db: db_dependency,
    user: user_dependency
):
    """
    Update item quantity in cart
    """
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Find the cart item
    cart_item = db.query(Cart).filter(
        Cart.accountid == user['accountid'],
        Cart.productid == product_id
    ).first()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Item not found in cart")

    if quantity < 1:
        raise HTTPException(status_code=400, detail="Quantity must be at least 1")

    # Update the quantity directly
    cart_item.quantity = quantity
    db.commit()
    return {"message": "Quantity updated", "quantity": quantity}
