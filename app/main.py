from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import planta
from app.core.config import settings
from app.routers.health import router as health_router
from app.routers.db_test import router as db_test_router
from app.routers.usuarios import router as usuarios_router
from app.routers.especie import router as especie_router
from app.routers.notificacao import router as notificacao_router
from app.routers.eventos import router as eventos_router
from app.routers import historico
from app.routers import cronograma
from app.routers import esp32

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8081",
        "https://croop.ddns.net",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(db_test_router)
app.include_router(usuarios_router)
app.include_router(planta.router)
app.include_router(especie_router)
app.include_router(notificacao_router)
app.include_router(eventos_router)


@app.get("/")
def root():
    return {"message": "Croop API running"}

app.include_router(historico.router)
app.include_router(cronograma.router)
app.include_router(esp32.router)