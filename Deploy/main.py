from fastapi import FastAPI, HTTPException, Depends, Header, Path
import uvicorn
from fastapi.middleware.cors import CORSMiddleware




import routes.products as products
import routes.services as services
import routes.cars as cars
import routes.account as account
import routes.transactions as transactions
import routes.admin as admin
import routes.appointments as appointments

app = FastAPI(title="TayarPro API",
              description="API for TayarPro", version="1.0.0")

# Allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # This allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # This allows all HTTP methods
    allow_headers=["*"],  # This allows all headers
)



"""
Compile the Routing Files Together
"""

app.include_router(account.router)
app.include_router(products.router)
app.include_router(services.router)
app.include_router(cars.router)
app.include_router(transactions.router)
app.include_router(admin.router)
app.include_router(appointments.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}


# class UserRegisterRequestV2(BaseModel):
#     email: EmailStr = Field(..., example="rahmanrom@gmail.com")
#     password: str = Field(..., example="123456")
#     first_name: str = Field(..., example="HJ")
#     last_name: str = Field(..., example="Wong")


# @app.post("/register-v2", tags=["Authentication"])
# async def register_user_v2(user: UserRegisterRequestV2, db: db_dependency):
#     """
#     Important Point:

#     Date is in ISO 8601 Format (Recommended): 1990-12-31 (Year-Month-Day)
#     """
#     if db.query(User).filter(User.email == user.email).first():
#         raise HTTPException(status_code=400, detail="Email already registered")

#     accountid = str(uuid.uuid4())

#     new_user = User(
#         accountid=accountid,
#         firstname=user.first_name,
#         lastname=user.last_name,
#         username=user.email,
#         email=user.email,
#         password=bcrypt_context.hash(user.password),
#         createdat=datetime.now())
#     db.add(new_user)
#     db.commit()

#     return {
#         "message": "User successfully registered",
#         "user_info": new_user.to_dict()  # Use the to_dict method
#     }



if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8080)
