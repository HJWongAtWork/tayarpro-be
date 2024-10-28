from fastapi import APIRouter, Depends, Path, HTTPException
from fastapi.responses import RedirectResponse
router = APIRouter()


@router.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")
