from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Numeric, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SensorUmidade(Base):
    __tablename__ = "sensor_umidade"

    id_sensor: Mapped[int] = mapped_column(primary_key=True)
    id_dispositivo: Mapped[int] = mapped_column(ForeignKey("dispositivo_iot.id_dispositivo"), nullable=False)
    tipo_sensor: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    unidade_medida: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    status_sensor: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    data_instalacao: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    calibracao_min: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    calibracao_max: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)

    # Relationships
    dispositivo: Mapped["DispositivoIot"] = relationship(back_populates="sensores")
    leituras: Mapped[list["LeituraUmidade"]] = relationship(back_populates="sensor")