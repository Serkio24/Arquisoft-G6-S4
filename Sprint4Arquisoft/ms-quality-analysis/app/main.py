from fastapi import FastAPI
from app.api import quality, health

app = FastAPI(
    title="ms-quality-analysis",
    description="Microservicio de análisis de calidad y mantenibilidad — BITE.co",
    version="1.0.0",
)

app.include_router(health.router)
app.include_router(quality.router, prefix="/quality")
