from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario: Mapped[int] = mapped_column(primary_key=True, index=True)

    nome: Mapped[str] = mapped_column(String(100), nullable=False)

    email: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        nullable=False,
        index=True
    )

    cpf: Mapped[str] = mapped_column(
        String(11),
        unique=True,
        nullable=False
    )

    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    data_cadastro: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    ultimo_login: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    status_conta: Mapped[str] = mapped_column(
        String(30),
        nullable=True,
        default="ativo"
    )

    preferencia_notificacao: Mapped[str] = mapped_column(
        String(50),
        nullable=True
    )