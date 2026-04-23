from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ItemCronograma(Base):
    __tablename__ = "item_cronograma"

    id_item_cronograma: Mapped[int] = mapped_column(primary_key=True)
    id_cronograma: Mapped[int] = mapped_column(ForeignKey("cronograma_cuidado.id_cronograma"), nullable=False)
    tipo_cuidado: Mapped[str] = mapped_column(String(50), nullable=False)
    descricao: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    data_prevista: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status_execucao: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    data_execucao: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    origem_item: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Relationships
    cronograma: Mapped["CronogramaCuidado"] = relationship(back_populates="itens")
