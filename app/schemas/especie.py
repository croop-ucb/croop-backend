from pydantic import BaseModel
from typing import Optional


class EspecieResponse(BaseModel):
    id_especie: int
    nome_comum: str
    nome_cientifico: Optional[str] = None
    descricao: Optional[str] = None
    faixa_umidade_min: Optional[float] = None
    faixa_umidade_max: Optional[float] = None
    frequencia_media_irrigacao: Optional[int] = None
    necessidade_luz: Optional[str] = None
    observacoes_cuidado: Optional[str] = None

    model_config = {"from_attributes": True}
