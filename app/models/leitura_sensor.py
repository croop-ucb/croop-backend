from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class LeituraSensor(Base):
    __tablename__ = "leitura_sensor"

    id_leitura: Mapped[int] = mapped_column(primary_key=True)
    id_planta: Mapped[int] = mapped_column(
        ForeignKey("plantas.id_planta"), nullable=False, index=True
    )
    umidade_percentual: Mapped[float] = mapped_column(Float, nullable=False)
    adc_bruto: Mapped[int] = mapped_column(Integer, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
