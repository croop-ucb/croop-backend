from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, Numeric, String, Text, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Irrigacao(Base):
    __tablename__ = "irrigacao"

    id_irrigacao: Mapped[int] = mapped_column(primary_key=True)
    id_planta: Mapped[int] = mapped_column(ForeignKey("plantas.id_planta"), nullable=False)
    id_dispositivo: Mapped[int] = mapped_column(ForeignKey("dispositivo_iot.id_dispositivo"), nullable=False)
    id_bomba: Mapped[int] = mapped_column(ForeignKey("bomba_dagua.id_bomba"), nullable=False)
    tipo_irrigacao: Mapped[str] = mapped_column(String(20), nullable=False)
    origem_decisao: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    data_hora_inicio: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    data_hora_fim: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    duracao_segundos: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    volume_estimado: Mapped[Optional[float]] = mapped_column(Numeric(8, 2), nullable=True)
    status_execucao: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    observacao: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    planta: Mapped["Planta"] = relationship(back_populates="irrigacoes")
    dispositivo: Mapped["DispositivoIot"] = relationship(back_populates="irrigacoes")
    bomba: Mapped["BombaDagua"] = relationship(back_populates="irrigacoes")
