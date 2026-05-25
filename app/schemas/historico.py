from datetime import datetime

from pydantic import BaseModel


class HistoricoItemResponse(BaseModel):
    tipo: str
    descricao: str
    data_hora: datetime


class HistoricoResponse(BaseModel):
    pagina: int
    limite: int
    total: int
    registros: list[HistoricoItemResponse]