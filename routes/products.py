from fastapi import APIRouter, Depends, Path, HTTPException
router = APIRouter()


@router.get("/products")
async def product():
    return {"message": "This is All Products"}
