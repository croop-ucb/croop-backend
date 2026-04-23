from datetime import date, datetime
from typing import Optional

from sqlalchemy import Boolean, Date, DateTime, String, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
import sqlalchemy as sa

from app.db.base import Base


class CronogramaCuidado(Base):
    __tablename__ = "cronograma_cuidado"

    id_cronograma: Mapped[int] = mapped_column(primary_key=True)
    id_planta: Mapped[int] = mapped_column(ForeignKey("plantas.id_planta"), nullable=False)
    data_geracao: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    periodo_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    periodo_fim: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    descricao_resumida: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=sa.text("true"))

    # Relationships
    planta: Mapped["Planta"] = relationship(back_populates="cronogramas")
    itens: Mapped[list["ItemCronograma"]] = relationship(back_populates="cronograma")
