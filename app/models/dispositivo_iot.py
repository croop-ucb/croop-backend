from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, String, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class DispositivoIot(Base):
    __tablename__ = "dispositivo_iot"

    id_dispositivo: Mapped[int] = mapped_column(primary_key=True)
    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuarios.id_usuario"), nullable=False)
    codigo_serie: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    nome_dispositivo: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status_dispositivo: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    data_ativacao: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    ultima_comunicacao: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    wifi_configurado: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    local_instalacao: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)

    # Relationships
    usuario: Mapped["Usuario"] = relationship(back_populates="dispositivos")
    sensores: Mapped[list["SensorUmidade"]] = relationship(back_populates="dispositivo")
    bombas: Mapped[list["BombaDagua"]] = relationship(back_populates="dispositivo")
    vinculos: Mapped[list["VinculoPlantaDispositivo"]] = relationship(back_populates="dispositivo")
    irrigacoes: Mapped[list["Irrigacao"]] = relationship(back_populates="dispositivo")