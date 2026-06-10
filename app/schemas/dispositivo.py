from pydantic import BaseModel


class GerarTokenRequest(BaseModel):
    planta_id: int


class GerarTokenResponse(BaseModel):
    token: str
    expires_in: int


class AtivarDispositivoRequest(BaseModel):
    token: str
    codigo_serie: str


class AtivarDispositivoResponse(BaseModel):
    planta_id: int
