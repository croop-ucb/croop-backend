from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
import sqlalchemy as sa

from app.db.base import Base


class VinculoPlantaDispositivo(Base):
    __tablename__ = "vinculo_planta_dispositivo"

    id_vinculo: Mapped[int] = mapped_column(primary_key=True)
    id_planta: Mapped[int] = mapped_column(ForeignKey("plantas.id_planta"), nullable=False)
    id_dispositivo: Mapped[int] = mapped_column(ForeignKey("dispositivo_iot.id_dispositivo"), nullable=False)
    data_inicio: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    data_fim: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=sa.text("true"))

    # Relationships
    planta: Mapped["Planta"] = relationship(back_populates="vinculos")
    dispositivo: Mapped["DispositivoIot"] = relationship(back_populates="vinculos")
