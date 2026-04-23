from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, String, Text, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
import sqlalchemy as sa

from app.db.base import Base


class Notificacao(Base):
    __tablename__ = "notificacao"

    id_notificacao: Mapped[int] = mapped_column(primary_key=True)
    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuarios.id_usuario"), nullable=False)
    id_planta: Mapped[Optional[int]] = mapped_column(ForeignKey("plantas.id_planta"), nullable=True)
    tipo_notificacao: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    titulo: Mapped[str] = mapped_column(String(150), nullable=False)
    mensagem: Mapped[str] = mapped_column(Text, nullable=False)
    data_envio: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    lida: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=sa.text("false"))
    canal_envio: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)

    # Relationships
    usuario: Mapped["Usuario"] = relationship(back_populates="notificacoes")
    planta: Mapped[Optional["Planta"]] = relationship(back_populates="notificacoes")
