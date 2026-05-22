from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class NotificacaoResponse(BaseModel):
    id_notificacao: int
    id_planta: Optional[int]
    tipo_notificacao: Optional[str]
    titulo: str
    mensagem: str
    data_envio: datetime
    lida: bool

    class Config:
        from_attributes = True