from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class LeituraSensorCreate(BaseModel):
    planta_id: int
    umidade_percentual: float
    adc_bruto: int


class LeituraSensorResponse(BaseModel):
    id_leitura: int
    id_planta: int
    umidade_percentual: float
    adc_bruto: int
    timestamp: datetime

    model_config = {"from_attributes": True}


class EventoIrrigacaoCreate(BaseModel):
    planta_id: int
    duracao_segundos: int


class EventoIrrigacaoResponse(BaseModel):
    id_evento: int
    id_planta: int
    duracao_segundos: int
    timestamp: datetime

    model_config = {"from_attributes": True}


class ComandoIrrigacaoCreate(BaseModel):
    planta_id: int


class ComandoIrrigacaoResponse(BaseModel):
    id_comando: int
    id_planta: int
    pendente: bool
    criado_em: datetime

    model_config = {"from_attributes": True}


class IrrigarResponse(BaseModel):
    mensagem: str
    comando: ComandoIrrigacaoResponse


class ComandoESP32Response(BaseModel):
    irrigar: bool
    umidade_minima: float
    umidade_maxima: float


class UltimaLeituraStatus(BaseModel):
    umidade_percentual: float
    adc_bruto: int
    timestamp: datetime

    model_config = {"from_attributes": True}


class UltimaIrrigacaoStatus(BaseModel):
    duracao_segundos: int
    timestamp: datetime

    model_config = {"from_attributes": True}


class StatusPlantaResponse(BaseModel):
    ultima_leitura: Optional[UltimaLeituraStatus]
    ultimo_evento_irrigacao: Optional[UltimaIrrigacaoStatus]
    tem_comando_pendente: bool
    dispositivo_online: bool
