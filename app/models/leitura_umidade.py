from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Numeric, String, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class LeituraUmidade(Base):
    __tablename__ = "leitura_umidade"

    id_leitura: Mapped[int] = mapped_column(primary_key=True)
    id_sensor: Mapped[int] = mapped_column(ForeignKey("sensor_umidade.id_sensor"), nullable=False)
    id_planta: Mapped[int] = mapped_column(ForeignKey("plantas.id_planta"), nullable=False)
    valor_umidade: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    data_hora_leitura: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    status_leitura: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    origem_leitura: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Relationships
    sensor: Mapped["SensorUmidade"] = relationship(back_populates="leituras")
    planta: Mapped["Planta"] = relationship(back_populates="leituras")
