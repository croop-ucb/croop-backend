from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, String, Text, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RecomendacaoIA(Base):
    __tablename__ = "recomendacao_ia"

    id_recomendacao: Mapped[int] = mapped_column(primary_key=True)
    id_planta: Mapped[int] = mapped_column(ForeignKey("plantas.id_planta"), nullable=False)
    data_geracao: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    tipo_recomendacao: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    descricao_recomendacao: Mapped[str] = mapped_column(Text, nullable=False)
    nivel_prioridade: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    status_recomendacao: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    justificativa: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    planta: Mapped["Planta"] = relationship(back_populates="recomendacoes")
