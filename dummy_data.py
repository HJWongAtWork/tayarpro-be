import time
from models import Notification
import uuid
from passlib.context import CryptContext
import string
from faker import Faker
import random
from datetime import datetime, timedelta
from database import SessionLocal
from models import Car, User, Tyre, Service, RegisterCar, Orders, OrdersDetail, Appointment
from datetime import datetime


# Create a new session
session = SessionLocal()

"""
1. Generate 1,000 User Accounts.
2, Register a car for the user.
2. Automate 100,000 Transactions.
"""


def get_random_date(
    start_date: str = "01-01-2018",
    end_date: str = "24-11-2024",
    date_format: str = "%d-%m-%Y"
) -> str:
    """
    Generate a random date between two specified dates.

    Parameters:
    - start_date (str): The start date in string format. Defaults to "01-01-2018".
    - end_date (str): The end date in string format. Defaults to "24-11-2024".
    - date_format (str): The date format to parse the input dates.

    Returns:
    - str: Random date between the start and end dates, formatted as 'YYYY-MM-DD'.
    """
    # Convert strings to datetime objects
    start = datetime.strptime(start_date, date_format)
    end = datetime.strptime(end_date, date_format)

    # Calculate the range in days between start and end
    delta_days = (end - start).days

    # Generate a random number of days within the range
    random_days = random.randint(0, delta_days)

    # Generate the random date
    random_date = start + timedelta(days=random_days)

    # Return date in 'YYYY-MM-DD' format
    return random_date.strftime("%Y-%m-%d")


def get_random_time() -> str:
    """
    Generate a random time between 09:00 and 16:00, with minutes always set to :00.

    Returns:
    - str: Random time in 'HH:MM' (24-hour) format.
    """
    # Generate a random hour between 9 and 16 (inclusive)
    random_hour = random.randint(9, 16)

    # Format the time as 'HH:00'
    random_time = f"{random_hour:02d}:00"

    return random_time


all_cars = [[car.car_brand, car.car_model, car.tyre_size, car.car_year, car.car_type]
            for car in session.query(Car).all()]

# Initialize Faker instance
fake = Faker('en_MS')
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
lst_email = []

for i in range(250):
    email = fake.email()  # Generate a random email address

    if email in lst_email:
        email = fake.email()
        lst_email.append(email)
    else:
        lst_email.append(email)

    # Generate a random 12-character password
    password = '123456'
    first_name = fake.first_name()  # Generate a random first name
    last_name = fake.last_name()  # Generate a random last name'

    user = User(accountid=str(uuid.uuid4()), email=email, password=bcrypt_context.hash(password),
                firstname=first_name, lastname=last_name, username=email, createdat=get_random_date(start_date='01-01-2020') + " " + get_random_time())

    session.add(user)
    session.commit()

    plate_number = fake.license_plate()
    plate_number = plate_number.replace(" ", "").lower().replace("-", "")

    for k in range(random.randint(1, 3)):

        selected_car = random.choice(all_cars)
        car = RegisterCar(platenumber=plate_number, carbrand=selected_car[0], carmodel=selected_car[1],
                          tyresize=selected_car[2], caryear=selected_car[3], accountid=user.accountid, cartype=selected_car[4], createdat=datetime.now())
        session.add(car)
        session.commit()

    print(f"User {i} created")


# Generate random data
new_user = User(accountid=str(uuid.uuid4()), isAdmin='Y', email="rahmanrom@gmail.com", password=bcrypt_context.hash("123456"),
                firstname="Rahman", lastname="Rom", username="rahmanrom@gmail.com", createdat=get_random_date() + " " + get_random_time())
session.add(new_user)
session.commit()

two_plates = ["wyd1234", "wyd1235"]

for plate in two_plates:
    selected_car = random.choice(all_cars)
    car = RegisterCar(platenumber=plate, carbrand=selected_car[0], carmodel=selected_car[1],
                      tyresize=selected_car[2], caryear=selected_car[3], accountid=new_user.accountid, cartype=selected_car[4], createdat=datetime.now())
    session.add(car)
    session.commit()


tyre_ids = [tyre.itemid for tyre in session.query(Tyre).all()]
service_ids = [service.serviceid for service in session.query(Service).all()]
user_ids = [user.accountid for user in session.query(User).all()]
print(user_ids)

for i in range(2843):
    random_user_id = random.choice(user_ids)
    lst_car = [car.carid for car in session.query(RegisterCar).filter(
        RegisterCar.accountid == random_user_id).all()]
    selected_car_id = random.choice(lst_car)
    random_number_of_tyres = random.randint(1, 2)
    random_tyre_ids = random.sample(tyre_ids, random_number_of_tyres)
    random_service_id = random.choice(service_ids)

    """
    1. Create Order First
    2. Create Order Details
    3. Create Order Service
    """

    user_details = session.query(User).filter(
        User.accountid == random_user_id).first()
    date_created = user_details.createdat
    print(date_created)
    convert_date_to_string = date_created.strftime("%d-%m-%Y")

    order_id = str(uuid.uuid4())
    appointment_date = get_random_date(start_date=convert_date_to_string)
    appointment_time = get_random_time()
    appointment_bay = random.randint(1, 5)

    # Create Order
    order = Orders(
        orderid=order_id,
        accountid=random_user_id,
        createdat=appointment_date + ' ' + appointment_time,
        paymentmethod=random.choice(['Cash', 'Card', 'E-Wallet']),

    )

    session.add(order)
    session.commit()

    for tyre_id in random_tyre_ids:
        random_quantity = random.randint(1, 3)
        unit_price = session.query(Tyre).filter(
            Tyre.itemid == tyre_id).first().unitprice
        order_detail = OrdersDetail(
            orderid=order_id,
            productid=tyre_id,
            quantity=random_quantity,
            totalprice=unit_price * random_quantity,
            unitprice=unit_price
        )

        session.add(order_detail)
        session.commit()

    add_service = OrdersDetail(
        orderid=order_id,
        productid=random_service_id,
        quantity=1,
        totalprice=session.query(Service).filter(
            Service.serviceid == random_service_id).first().price,
        unitprice=session.query(Service).filter(
            Service.serviceid == random_service_id).first().price
    )

    session.add(add_service)
    session.commit()

    appointment_id = str(uuid.uuid4())
    appointment = Appointment(
        appointmentid=appointment_id,
        accountid=random_user_id,
        appointmentdate=appointment_date + ' ' + appointment_time,
        createdat=datetime.now(),
        status='Future',
        appointment_bay=appointment_bay,
        carid=selected_car_id
    )

    session.add(appointment)
    session.commit()

    # Update the Order ID for the new appointment
    appointment.orderid = order_id

    # Calculate the total price for the appointment
    total_price = sum(detail.totalprice for detail in session.query(
        OrdersDetail).filter(OrdersDetail.orderid == order_id).all())

    # Update the total price in the Orders table
    order.totalprice = total_price
    order.appointmentid = appointment_id

    session.commit()

    import random


# Create a new session
session = SessionLocal()


"""
Things to do:-

"""

notifications = [
    {
        "message": "Received new order from lol@gmail.com!",
        "status": "active",
        "category": "Order",
        "icon": "fa fa-shopping-cart",
    },
    {
        "message": "Uh oh! Tyre T002 stock is running low!",
        "status": "active",
        "category": "Stock",
        "icon": "fa fa-exclamation-triangle",
    },
    {
        "message": "aniq@gmail.com has just registered!",
        "status": "active",
        "category": "User",
        "icon": "fa fa-user-plus",
    },
    {
        "message": "New order placed by vincent.23@example.com!",
        "status": "active",
        "category": "Order",
        "icon": "fa fa-shopping-cart",
    },
    {
        "message": "Stock for Tyre T008 is below threshold!",
        "status": "active",
        "category": "Stock",
        "icon": "fa fa-exclamation-triangle",
    },
    {
        "message": "vincent.1@example.com has just registered!",
        "status": "active",
        "category": "User",
        "icon": "fa fa-user-plus",
    },
    {
        "message": "Received new order from 33@example.org!",
        "status": "active",
        "category": "Order",
        "icon": "fa fa-shopping-cart",
    },
    {
        "message": "Stock for Tyre T008 is running low!",
        "status": "active",
        "category": "Stock",
        "icon": "fa fa-exclamation-triangle",
    },
    {
        "message": "christopher3220@example.org has just registered!",
        "status": "active",
        "category": "User",
        "icon": "fa fa-user-plus",
    },
    {
        "message": "New order placed by aniqfaidi@example.com!",
        "status": "active",
        "category": "Order",
        "icon": "fa fa-shopping-cart",
    }
]

for notification in notifications:
    new_notification = Notification(
        notificationid=str(uuid.uuid4()),
        message=notification["message"],
        status=notification["status"],
        category=notification["category"],
        icon=notification["icon"],
        createdat=datetime.now()
    )
    session.add(new_notification)
    session.commit()
    time.sleep(1)
