from datetime import date, datetime

from pydantic import BaseModel


class ItemCronogramaResponse(BaseModel):
    id_item_cronograma: int
    tipo_cuidado: str
    descricao: str | None
    data_prevista: datetime
    status_execucao: str | None

    class Config:
        from_attributes = True


class CronogramaResponse(BaseModel):
    id_cronograma: int
    id_planta: int
    frequencia_semanal: int
    dias_sugeridos: list[str]
    horario_sugerido: str
    nivel_prioridade: str
    observacoes: str
    justificativa: str
    periodo_inicio: date
    periodo_fim: date | None
    itens: list[ItemCronogramaResponse]
