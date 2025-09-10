from fastapi import FastAPI
from app.routers import orders

app = FastAPI(title = "media-kiosk-backend", version = "1.0.0")

app.include_router(orders.router, prefix="/api/v1/orders", tags=["Orders"])
