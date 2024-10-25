from fastapi import APIRouter, Depends, Path, HTTPException
from fastapi.responses import RedirectResponse
router = APIRouter()


@router.post("/login")
async def login():
    return {"message": "This is Login Endpoint"}


@router.post("/register")
async def register():
    return {"message": "This is Register Endpoint"}


@router.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")
