from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, String, Text, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class HistoricoCuidado(Base):
    __tablename__ = "historico_cuidado"

    id_historico: Mapped[int] = mapped_column(primary_key=True)
    id_planta: Mapped[int] = mapped_column(ForeignKey("plantas.id_planta"), nullable=False)
    tipo_evento: Mapped[str] = mapped_column(String(50), nullable=False)
    descricao_evento: Mapped[str] = mapped_column(Text, nullable=False)
    data_hora_evento: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    origem_evento: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Relationships
    planta: Mapped["Planta"] = relationship(back_populates="historicos")
