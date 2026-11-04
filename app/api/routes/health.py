from fastapi import APIRouter

from app.schemas import Health

router = APIRouter(tags=["health"])


@router.get("/health", response_model=Health)
async def health():
    """Liveness check for hosting platforms and monitoring."""
    return Health()
