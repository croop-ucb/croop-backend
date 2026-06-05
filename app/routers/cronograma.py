import re
from datetime import timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.cronograma_cuidado import CronogramaCuidado
from app.models.item_cronograma import ItemCronograma
from app.models.planta import Planta
from app.models.recomendacao_ia import RecomendacaoIA
from app.schemas.cronograma import CronogramaResponse
from app.services.cronograma_service import gerar_e_persistir_cronograma

router = APIRouter(prefix="/plantas", tags=["Cronograma"])

_DAY_NAMES = ["segunda", "terca", "quarta", "quinta", "sexta", "sabado", "domingo"]


@router.get("/{planta_id}/cronograma", response_model=CronogramaResponse)
def obter_cronograma(
    planta_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    planta = (
        db.query(Planta)
        .filter(Planta.id_planta == planta_id, Planta.id_usuario == user["id_usuario"])
        .first()
    )
    if not planta:
        raise HTTPException(status_code=404, detail="Planta não encontrada")

    cronograma = (
        db.query(CronogramaCuidado)
        .filter(
            CronogramaCuidado.id_planta == planta_id,
            CronogramaCuidado.ativo.is_(True),
        )
        .order_by(CronogramaCuidado.data_geracao.desc())
        .first()
    )
    if not cronograma:
        raise HTTPException(status_code=404, detail="Nenhum cronograma ativo encontrado")

    itens = (
        db.query(ItemCronograma)
        .filter(ItemCronograma.id_cronograma == cronograma.id_cronograma)
        .order_by(ItemCronograma.data_prevista)
        .all()
    )

    recomendacao = (
        db.query(RecomendacaoIA)
        .filter(
            RecomendacaoIA.id_planta == planta_id,
            RecomendacaoIA.tipo_recomendacao == "cronograma_irrigacao",
        )
        .order_by(RecomendacaoIA.data_geracao.desc())
        .first()
    )

    frequencia_semanal = len(itens)
    dias_sugeridos = [
        _DAY_NAMES[item.data_prevista.astimezone(timezone.utc).weekday()]
        for item in itens
    ]
    match = re.search(r"(\d{2}:\d{2})$", cronograma.descricao_resumida or "")
    horario_sugerido = match.group(1) if match else "08:00"

    return {
        "id_cronograma": cronograma.id_cronograma,
        "id_planta": planta_id,
        "frequencia_semanal": frequencia_semanal,
        "dias_sugeridos": dias_sugeridos,
        "horario_sugerido": horario_sugerido,
        "nivel_prioridade": recomendacao.nivel_prioridade if recomendacao else "normal",
        "observacoes": recomendacao.descricao_recomendacao if recomendacao else "",
        "justificativa": recomendacao.justificativa if recomendacao else "",
        "periodo_inicio": cronograma.periodo_inicio,
        "periodo_fim": cronograma.periodo_fim,
        "itens": itens,
    }


@router.post("/{planta_id}/cronograma", response_model=CronogramaResponse)
def gerar_cronograma(
    planta_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    try:
        return gerar_e_persistir_cronograma(db, planta_id, user["id_usuario"])
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Não foi possível gerar o cronograma. Tente novamente.",
        )
