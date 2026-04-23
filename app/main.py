from fastapi import FastAPI

from app.core.config import settings
from app.routers.health import router as health_router
from app.routers.db_test import router as db_test_router

app = FastAPI(title=settings.app_name)

app.include_router(health_router)
app.include_router(db_test_router)


@app.get("/")
def root():
    return {"message": "Croop API running"}