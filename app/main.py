from fastapi import FastAPI
from app.routers import orders, menu

app = FastAPI(title = "media-kiosk-backend", version = "1.0.0")

app.include_router(orders.router, prefix="/api/v1/orders", tags=["Orders"])
app.include_router(menu.router, prefix="/api/v1/menu", tags=["Menu"])