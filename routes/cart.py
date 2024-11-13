from fastapi import APIRouter, Depends, Path, HTTPException
import models
from database import SessionLocal
from typing_extensions import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from decimal import Decimal

router = APIRouter()

#Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()






"""
View Cart Items
"""



# class AddToCart(BaseModel):
#     accountid:str
#     productid:str
#     unitprice: Decimal = Field(...,decimal_places=2)
#     quantity:int
#     description:str

# class CartItemUpdate (BaseModel):
#     quantity : int

# # ADD ITEM TO CART
# @router.post("/cart")
# async def add_to_cart(addToCart:AddToCart,db: Session = Depends(get_db)):
#     try:
#         # Check if the item already exists in the cart
#         existing_item = db.query(models.Cart).filter(
#             models.Cart.accountid == addToCart.accountid,
#             models.Cart.productid == addToCart.productid
#         ).first()

#         if existing_item:
#             # If the item exists, update the quantity
#             existing_item.quantity += addToCart.quantity
#             db.commit()
#             db.refresh(existing_item)
#             return existing_item
#         else:
#             # If the item doesn't exist, create a new entry
#             # max_itemlineno = db.query(func.max(models.Cart.itemlineno)).filter(models.Cart.accountid == addToCart.accountid).scalar()
#             # next_itemlineno = (max_itemlineno or 0) + 1
#             new_cart = models.Cart(
#                 accountid=addToCart.accountid,
#                 productid=addToCart.productid,
#                 unitprice=addToCart.unitprice,
#                 quantity=addToCart.quantity,
#                 description=addToCart.description
#             )
#             db.add(new_cart)
#             db.commit()
#             db.refresh(new_cart)
#             return new_cart
#     except Exception as e:
#         return {"error": str(e)}

# # DELETE CART ITEM
# @router.delete("/cart/{accountid}/{productid}")
# async def delete_cart_item(accountid: str, productid: str, db: Session = Depends(get_db)):
#     cart_item = db.query(models.Cart).filter(
#         models.Cart.accountid == accountid,
#         models.Cart.productid == productid
#     ).first()
#     if not cart_item:
#         return {"message": "Cart item not found"}
#     db.delete(cart_item)
#     db.commit()
#     return {"message": "Cart item deleted"}

# # GET CART BY ACCOUNT ID
# @router.get("/cart/{accountid}")
# async def get_cart_by_accountid(accountid: str, db: Session = Depends(get_db)):
#     cart = db.query(models.Cart).filter(models.Cart.accountid == accountid).all()
#     return cart

# # UPDATE CART ITEM 
# @router.put("/cart/{accountid}/{productid}")
# async def update_cart_item(accountid: str, productid: str, item_update: CartItemUpdate , db: Session = Depends(get_db)):
#     cart_item = db.query(models.Cart).filter(
#         models.Cart.accountid == accountid,
#         models.Cart.productid == productid
#     ).first()
#     if not cart_item:
#         return {"message": "Cart item not found"}
#     cart_item.quantity = item_update.quantity
#     db.commit()
#     db.refresh(cart_item)


# # GET CART ITEM DETAIL BY ACCOUNT ID AND PRODUCT ID 
# @router.get("/cart/{accountid}/{productid}")
# async def get_cart_by_accountid_and_productid(accountid: str, productid: str, db: Session = Depends(get_db)):
#     cart = db.query(models.Cart).filter(
#         models.Cart.accountid == accountid,
#         models.Cart.productid == productid
#     ).first()
#     if not cart:
#         return {"message": "Cart item not found"}
#     return cart