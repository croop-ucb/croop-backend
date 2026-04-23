from sqlalchemy import String, Text, DateTime, Boolean, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.vinculo_planta_dispositivo import VinculoPlantaDispositivo
    from app.models.irrigacao import Irrigacao
    from app.models.leitura_umidade import LeituraUmidade
    from app.models.historico_cuidado import HistoricoCuidado
    from app.models.recomendacao_ia import RecomendacaoIA
    from app.models.cronograma_cuidado import CronogramaCuidado
    from app.models.notificacao import Notificacao


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
    vinculos: Mapped[list["VinculoPlantaDispositivo"]] = relationship(back_populates="planta")
    irrigacoes: Mapped[list["Irrigacao"]] = relationship(back_populates="planta")
    leituras: Mapped[list["LeituraUmidade"]] = relationship(back_populates="planta")
    historicos: Mapped[list["HistoricoCuidado"]] = relationship(back_populates="planta")
    recomendacoes: Mapped[list["RecomendacaoIA"]] = relationship(back_populates="planta")
    cronogramas: Mapped[list["CronogramaCuidado"]] = relationship(back_populates="planta")
    notificacoes: Mapped[list["Notificacao"]] = relationship(back_populates="planta")
    