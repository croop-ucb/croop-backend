from fastapi import APIRouter, Depends
from sqlalchemy import union_all, select, literal, cast, String, func
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import get_current_user

from app.models.historico_cuidado import HistoricoCuidado
from app.models.leitura_umidade import LeituraUmidade
from app.models.notificacao import Notificacao
from app.models.planta import Planta

from app.schemas.historico import HistoricoResponse

router = APIRouter(
    prefix="/historico",
    tags=["Histórico"]
)


@router.get("/", response_model=HistoricoResponse)
def consultar_historico(
    pagina: int = 1,
    limite: int = 10,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    id_usuario = user["id_usuario"]

    q1 = (
        select(
            HistoricoCuidado.tipo_evento.label("tipo"),
            HistoricoCuidado.descricao_evento.label("descricao"),
            HistoricoCuidado.data_hora_evento.label("data_hora"),
        )
        .join(Planta, HistoricoCuidado.id_planta == Planta.id_planta)
        .where(Planta.id_usuario == id_usuario)
    )

    q2 = (
        select(
            literal("leitura_umidade").label("tipo"),
            func.concat("Umidade registrada: ", cast(LeituraUmidade.valor_umidade, String), "%").label("descricao"),
            LeituraUmidade.data_hora_leitura.label("data_hora"),
        )
        .join(Planta, LeituraUmidade.id_planta == Planta.id_planta)
        .where(Planta.id_usuario == id_usuario)
    )

    q3 = (
        select(
            literal("notificacao").label("tipo"),
            Notificacao.mensagem.label("descricao"),
            Notificacao.data_envio.label("data_hora"),
        )
        .where(Notificacao.id_usuario == id_usuario)
    )

    combined = union_all(q1, q2, q3).subquery()

    total = db.execute(select(func.count()).select_from(combined)).scalar()

    rows = db.execute(
        select(combined)
        .order_by(combined.c.data_hora.desc())
        .limit(limite)
        .offset((pagina - 1) * limite)
    ).mappings().all()

    return {
        "pagina": pagina,
        "limite": limite,
        "total": total,
        "registros": [dict(row) for row in rows],
    }
