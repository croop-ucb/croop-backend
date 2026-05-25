from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import get_current_user

from app.models.historico_cuidado import HistoricoCuidado
from app.models.leitura_umidade import LeituraUmidade
from app.models.notificacao import Notificacao
from app.models.planta import Planta

from app.schemas.historico import (
    HistoricoItemResponse,
    HistoricoResponse
)

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

    historico_final = []

    # =========================
    # Histórico de cuidados
    # =========================

    historicos = (
        db.query(HistoricoCuidado)
        .join(Planta)
        .filter(Planta.id_usuario == id_usuario)
        .all()
    )

    for item in historicos:
        historico_final.append({
            "tipo": item.tipo_evento,
            "descricao": item.descricao_evento,
            "data_hora": item.data_hora_evento
        })

    # =========================
    # Leituras de umidade
    # =========================

    leituras = (
        db.query(LeituraUmidade)
        .join(Planta)
        .filter(Planta.id_usuario == id_usuario)
        .all()
    )

    for leitura in leituras:
        historico_final.append({
            "tipo": "leitura_umidade",
            "descricao": f"Umidade registrada: {leitura.valor_umidade}%",
            "data_hora": leitura.data_hora_leitura
        })

    # =========================
    # Notificações
    # =========================

    notificacoes = (
        db.query(Notificacao)
        .join(Planta)
        .filter(Planta.id_usuario == id_usuario)
        .all()
    )

    for notificacao in notificacoes:
        historico_final.append({
            "tipo": "notificacao",
            "descricao": notificacao.mensagem,
            "data_hora": notificacao.data_hora_envio
        })

    # =========================
    # Ordenar por data
    # =========================

    historico_final.sort(
        key=lambda item: item["data_hora"],
        reverse=True
    )

    # =========================
    # Paginação
    # =========================

    total = len(historico_final)

    inicio = (pagina - 1) * limite
    fim = inicio + limite

    registros_paginados = historico_final[inicio:fim]

    return {
        "pagina": pagina,
        "limite": limite,
        "total": total,
        "registros": registros_paginados
    }