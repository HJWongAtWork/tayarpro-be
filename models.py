from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Date, Enum, Numeric, Text
from database import Base, engine
from sqlalchemy.orm import relationship
import sys


class User(Base):
    __tablename__ = "users"
    accountid = Column(String(255), primary_key=True, index=True)
    firstname = Column(String(255), nullable=True)
    lastname = Column(String(255), nullable=True)
    username = Column(String(255), nullable=False, unique=True)
    phonenumber = Column(String(15), nullable=True)
    email = Column(String(255), nullable=False, unique=True)
    address = Column(String(255), nullable=True)
    state = Column(String(255), nullable=True)
    city = Column(String(255), nullable=True)
    zipcode = Column(Numeric(15), nullable=True)
    gender = Column(String(255), nullable=True)
    fullname = Column(String(255), nullable=True)
    password = Column(String(255), nullable=False)
    isAdmin = Column(String(255), default="N", nullable=False)
    createdat = Column(DateTime, nullable=False)
    isActive = Column(String(255), nullable=False, default="Y")

    def to_dict(self):
        return {
            "accountid": self.accountid,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "username": self.username,
            "phonenumber": self.phonenumber,
            "email": self.email}


class RegisterCar(Base):
    __tablename__ = "registercar"
    carid = Column(Integer, primary_key=True, autoincrement=True)
    accountid = Column(String(255), ForeignKey(
        "users.accountid"), nullable=False)
    carbrand = Column(String(255), nullable=False)
    carmodel = Column(String(255), nullable=False)
    caryear = Column(Integer, nullable=False)
    platenumber = Column(String(255), nullable=False)
    tyresize = Column(String(255), nullable=True)
    cartype = Column(String(255), nullable=True)
    createdat = Column(DateTime, nullable=True)
    isActive = Column(String(255), nullable=False, default="Y")


class Car(Base):
    __tablename__ = "car_specifications"
    # Define the column in the table
    car_id = Column(Integer, primary_key=True, index=True)
    car_brand = Column(String(255), nullable=False)
    car_model = Column(String(255), nullable=False)
    car_year = Column(Integer, nullable=False)
    tyre_size = Column(String(255), nullable=False)
    car_type = Column(String(255), nullable=False)


class Feedback (Base):
    __tablename__ = "feedback"
    feedbackid = Column(String(255), primary_key=True,
                        index=True, nullable=False)
    email = Column(String(255), ForeignKey("users.email"), nullable=False)
    subject = Column(String(255), nullable=False)
    content = Column(String(255), nullable=False)
    createdat = Column(DateTime, nullable=False)


class PaymentMethod(Base):
    __tablename__ = "paymentmethod"
    methodid = Column(String(255), primary_key=True)
    description = Column(String(255))
    status = Column(String(255))
    createdat = Column(DateTime)


class Products(Base):
    __tablename__ = "products"
    productid = Column(String(255), primary_key=True, nullable=False)
    description = Column(String(255), nullable=True)
    status = Column(String(255), nullable=True)
    createdby = Column(String(255), ForeignKey(
        "users.accountid"), nullable=True)
    createdat = Column(DateTime, nullable=True)


class Brands(Base):
    __tablename__ = "brands"
    brandid = Column(String(255), primary_key=True, nullable=False)
    productid = Column(String(255), ForeignKey(
        "products.productid"), nullable=False)
    description = Column(String(255), nullable=True)
    status = Column(String(255), nullable=True)
    createdat = Column(DateTime, nullable=True)
    createdby = Column(String(255), ForeignKey(
        "users.accountid"), nullable=True)

    tyres = relationship("Tyre", back_populates="brand")


class Tyre(Base):
    __tablename__ = "tyre"
    itemid = Column(String(255), primary_key=True,  nullable=False)
    productid = Column(String(255), ForeignKey(
        "products.productid"), nullable=False)
    brandid = Column(String(255), ForeignKey("brands.brandid"), nullable=False)
    description = Column(String(255), nullable=False)
    cartype = Column(String(255), nullable=False)
    image_link = Column(Text, nullable=False)
    unitprice = Column(Numeric(8, 2), nullable=False)
    details = Column(String, index=True, nullable=False, server_default='[]')
    tyresize = Column(String(255), nullable=False)
    speedindex = Column(String(255), nullable=False)
    loadindex = Column(Numeric(15), nullable=False)
    stockunit = Column(Numeric(15), nullable=False)
    status = Column(String(255), nullable=False, default="Active")
    createdby = Column(String(255), ForeignKey(
        "users.accountid"), nullable=True)
    createdat = Column(DateTime, nullable=True)

    brand = relationship("Brands", back_populates="tyres")


class ServiceType(Base):
    __tablename__ = "servicetype"
    typeid = Column(String(255), primary_key=True, nullable=False)
    description = Column(String(255), nullable=True)
    status = Column(String(255), nullable=True)
    createdat = Column(DateTime, nullable=True)
    createdby = Column(String(255), ForeignKey(
        "users.accountid"), nullable=True)


class Service(Base):
    __tablename__ = "service"
    serviceid = Column(String(255), primary_key=True, nullable=False)
    typeid = Column(String(255), ForeignKey(
        "servicetype.typeid"), nullable=False)
    description = Column(String(255), nullable=False)
    cartype = Column(String(255), nullable=False)
    price = Column(Numeric(8, 2), nullable=False)
    status = Column(String(255), nullable=False)
    createdby = Column(String(255), ForeignKey(
        "users.accountid"), nullable=True)
    createdat = Column(DateTime, nullable=True)
    image_link = Column(Text, nullable=True)


class Cart(Base):
    __tablename__ = "cart"
    accountid = Column(String(255), ForeignKey(
        "users.accountid"), primary_key=True)
    productid = Column(String(255), primary_key=True)
    description = Column(String(255), nullable=False)
    unitprice = Column(Numeric(8, 2), nullable=False)
    quantity = Column(Numeric(15, 0), nullable=False)


class Orders (Base):
    __tablename__ = "orders"
    orderid = Column(String(255), primary_key=True, nullable=False)
    accountid = Column(String(255), ForeignKey(
        "users.accountid"), nullable=False)
    createdat = Column(DateTime, nullable=False)
    totalprice = Column(Numeric(8, 2), nullable=True)
    appointmentid = Column(String(255), ForeignKey(
        "appointment.appointmentid"), nullable=True)
    # Pending, Completed, Cancelled
    status = Column(String(255), nullable=False, default="Pending")
    paymentmethod = Column(String(255), nullable=False)


class OrdersDetail(Base):
    __tablename__ = "ordersdetail"
    orderid = Column(String(255), ForeignKey("orders.orderid"),
                     primary_key=True, nullable=False)
    productid = Column(String(255), primary_key=True)
    carid = Column(Integer, ForeignKey(
        "registercar.carid"), nullable=True)
    unitprice = Column(Numeric(15, 0), nullable=False)
    quantity = Column(Numeric(15, 0), nullable=False)
    totalprice = Column(Numeric(8, 2), nullable=False)


class Appointment(Base):
    __tablename__ = "appointment"
    appointmentid = Column(String(255), primary_key=True, nullable=False)
    accountid = Column(String(255), ForeignKey(
        "users.accountid"), nullable=False)
    appointmentdate = Column(DateTime, nullable=False)
    createdat = Column(DateTime, nullable=False)
    # Completed, Cancelled, Future
    status = Column(String(255), nullable=False)
    appointment_bay = Column(String(255), nullable=True)


class Invoice(Base):
    __tablename__ = "invoice"
    invoiceid = Column(String(255), primary_key=True, nullable=False)
    accountid = Column(String(255), ForeignKey(
        "users.accountid"), nullable=False)
    methodid = Column(String(255), nullable=False)
    createdat = Column(DateTime, nullable=False)
    orderid = Column(String(255), ForeignKey("orders.orderid"), nullable=False)
    totalprice = Column(Numeric(8, 2), nullable=False)


class Notification(Base):
    __tablename__ = "notification"
    notificationid = Column(String(255), primary_key=True, nullable=False)
    accountid = Column(String(255), ForeignKey(
        "users.accountid"), nullable=True)
    message = Column(String(255), nullable=False)
    createdat = Column(DateTime, nullable=False)
    status = Column(String(255), nullable=False)
    category = Column(String(255), nullable=False)
    icon = Column(String(255), nullable=False)


if __name__ == "__main__":
    if "--recreate" in sys.argv:
        Base.metadata.drop_all(bind=engine)
        print("Dropped all tables.")
    Base.metadata.create_all(bind=engine)
    print("Created all tables.")

else:
    Base.metadata.create_all(bind=engine)
    print("Created all tables.")


"""
TODO:

1. In Cart and OrderDetails: Put Category: Tyre or Service



Notification: -

1. Everytime Checkout is done: 
    - Check stocks. If less than 10 add notification data
    - Add notification data for new orders


2. Everytime registration is done:
    - Add notification data for new registration


"""
