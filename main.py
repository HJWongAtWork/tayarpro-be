from fastapi import FastAPI, HTTPException, Depends, Header, Path
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import routes.auth as auth
import routes.products as products
import routes.services as services
import routes.cars as cars
import routes.cart as cart
import routes.checkout as checkout

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
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(services.router)
app.include_router(cars.router)
app.include_router(cart.router)
app.include_router(checkout.router)


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
