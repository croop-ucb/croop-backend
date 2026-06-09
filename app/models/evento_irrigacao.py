from datetime import datetime

from sqlalchemy import DateTime, Integer, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class EventoIrrigacao(Base):
    __tablename__ = "evento_irrigacao"

    id_evento: Mapped[int] = mapped_column(primary_key=True)
    id_planta: Mapped[int] = mapped_column(
        ForeignKey("plantas.id_planta"), nullable=False, index=True
    )
    duracao_segundos: Mapped[int] = mapped_column(Integer, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
