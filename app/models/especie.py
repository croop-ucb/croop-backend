from sqlalchemy import String, Integer, Text, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Especie(Base):
    __tablename__ = "especies"

    id_especie: Mapped[int] = mapped_column(primary_key=True, index=True)

    nome_comum: Mapped[str] = mapped_column(String(100), nullable=False)

    nome_cientifico: Mapped[str | None] = mapped_column(String(150), nullable=True)

    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)

    faixa_umidade_min: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)

    faixa_umidade_max: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)

    frequencia_media_irrigacao: Mapped[int | None] = mapped_column(Integer, nullable=True)

    necessidade_luz: Mapped[str | None] = mapped_column(String(50), nullable=True)

    observacoes_cuidado: Mapped[str | None] = mapped_column(Text, nullable=True)