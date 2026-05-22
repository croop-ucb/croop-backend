from fastapi import FastAPI
<<<<<<< HEAD
=======
from fastapi.middleware.cors import CORSMiddleware
>>>>>>> 81c51251f8622653de5e3aaf8008e86db6258897
from app.routers import planta
from app.core.config import settings
from app.routers.health import router as health_router
from app.routers.db_test import router as db_test_router
from app.routers.usuarios import router as usuarios_router
from app.routers.especie import router as especie_router

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8081"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(db_test_router)
app.include_router(usuarios_router)
app.include_router(planta.router)
<<<<<<< HEAD
=======
app.include_router(especie_router)
>>>>>>> 81c51251f8622653de5e3aaf8008e86db6258897

@app.get("/")
def root():
    return {"message": "Croop API running"}