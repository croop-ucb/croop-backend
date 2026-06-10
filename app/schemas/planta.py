from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# 🔹 Base
class PlantaBase(BaseModel):
    id_especie: int = Field(..., description="Espécie é obrigatória")
    ambiente: str = Field(..., min_length=1, description="Ambiente é obrigatório")

    nome_personalizado: Optional[str] = None
    porte: Optional[str] = None
    localizacao_descricao: Optional[str] = None
    observacoes: Optional[str] = None
    ativa: Optional[bool] = True
    faixa_umidade_min: Optional[float] = Field(None, ge=0, le=100)
    faixa_umidade_max: Optional[float] = Field(None, ge=0, le=100)


# 🔹 Create
class PlantaCreate(PlantaBase):
    pass


# 🔹 Update
class PlantaUpdate(BaseModel):
    id_especie: Optional[int] = None
    nome_personalizado: Optional[str] = None
    porte: Optional[str] = None
    ambiente: Optional[str] = None
    localizacao_descricao: Optional[str] = None
    observacoes: Optional[str] = None
    ativa: Optional[bool] = None
    faixa_umidade_min: Optional[float] = Field(None, ge=0, le=100)
    faixa_umidade_max: Optional[float] = Field(None, ge=0, le=100)


# 🔹 Response
class PlantaResponse(PlantaBase):
    id_planta: int
    id_usuario: int
    data_cadastro: datetime

    class Config:
        from_attributes = True