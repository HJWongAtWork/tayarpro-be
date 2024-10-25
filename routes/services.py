from fastapi import APIRouter, Depends, Path, HTTPException
router = APIRouter()


@router.get("/services")
async def services():
    return {"message": "This is All Services"}
