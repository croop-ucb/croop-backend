from sqlalchemy import String, Text, DateTime, Boolean, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Planta(Base):
    __tablename__ = "plantas"

    id_planta: Mapped[int] = mapped_column(primary_key=True, index=True)

    id_usuario: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id_usuario"),
        nullable=False
    )

    id_especie: Mapped[int] = mapped_column(
        ForeignKey("especies.id_especie"),
        nullable=False
    )

    nome_personalizado: Mapped[str | None] = mapped_column(String(100), nullable=True)
    porte: Mapped[str | None] = mapped_column(String(30), nullable=True)
    ambiente: Mapped[str | None] = mapped_column(String(50), nullable=True)
    localizacao_descricao: Mapped[str | None] = mapped_column(String(200), nullable=True)

    data_cadastro: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    ativa: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=True)