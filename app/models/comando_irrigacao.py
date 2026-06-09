from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class ComandoIrrigacao(Base):
    __tablename__ = "comando_irrigacao"

    id_comando: Mapped[int] = mapped_column(primary_key=True)
    id_planta: Mapped[int] = mapped_column(
        ForeignKey("plantas.id_planta"), nullable=False, index=True
    )
    pendente: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
