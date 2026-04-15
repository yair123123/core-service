from fastapi import APIRouter

router = APIRouter(prefix="/offers", tags=["offers"])

@router.post("/new_offer", tags=["offers"])
async def new_offer()