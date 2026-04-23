from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Numeric, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class BombaDagua(Base):
    __tablename__ = "bomba_dagua"

    id_bomba: Mapped[int] = mapped_column(primary_key=True)
    id_dispositivo: Mapped[int] = mapped_column(ForeignKey("dispositivo_iot.id_dispositivo"), nullable=False)
    tipo_bomba: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    vazao: Mapped[Optional[float]] = mapped_column(Numeric(6, 2), nullable=True)
    status_bomba: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    data_instalacao: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    dispositivo: Mapped["DispositivoIot"] = relationship(back_populates="bombas")
    irrigacoes: Mapped[list["Irrigacao"]] = relationship(back_populates="bomba")
