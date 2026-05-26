from fastapi import APIRouter

router = APIRouter()


@router.get("/health", tags=["health"])
def health_check():
    """Kong y el load balancer usan este endpoint para verificar que el servicio está vivo."""
    return {"status": "ok", "service": "ms-quality-analysis"}
