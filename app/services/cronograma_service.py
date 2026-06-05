from datetime import date, datetime, time, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.cronograma_cuidado import CronogramaCuidado
from app.models.especie import Especie
from app.models.historico_cuidado import HistoricoCuidado
from app.models.item_cronograma import ItemCronograma
from app.models.leitura_umidade import LeituraUmidade
from app.models.planta import Planta
from app.models.recomendacao_ia import RecomendacaoIA
from app.services.ia_service import gerar_cronograma_ia

DAY_MAP = {
    "segunda": 0,
    "terca": 1,
    "quarta": 2,
    "quinta": 3,
    "sexta": 4,
    "sabado": 5,
    "domingo": 6,
}

REGENERACAO_INTERVALO_DIAS = 7


def _proximo_dia_semana(nome: str, a_partir: date) -> date:
    alvo = DAY_MAP.get(nome, 0)
    delta = (alvo - a_partir.weekday()) % 7
    return a_partir + timedelta(days=delta)


def deve_regenerar(db: Session, planta_id: int) -> bool:
    sete_dias_atras = datetime.now(timezone.utc) - timedelta(days=REGENERACAO_INTERVALO_DIAS)

    leitura_antiga = (
        db.query(LeituraUmidade)
        .filter(
            LeituraUmidade.id_planta == planta_id,
            LeituraUmidade.data_hora_leitura <= sete_dias_atras,
        )
        .first()
    )
    if not leitura_antiga:
        return False

    cronograma_ativo = (
        db.query(CronogramaCuidado)
        .filter(
            CronogramaCuidado.id_planta == planta_id,
            CronogramaCuidado.ativo.is_(True),
        )
        .first()
    )
    if not cronograma_ativo:
        return True

    limite_geracao = datetime.now(timezone.utc) - timedelta(days=REGENERACAO_INTERVALO_DIAS)
    return cronograma_ativo.data_geracao <= limite_geracao


def gerar_e_persistir_cronograma(db: Session, planta_id: int, id_usuario: int) -> dict:
    planta = (
        db.query(Planta)
        .filter(Planta.id_planta == planta_id, Planta.id_usuario == id_usuario)
        .first()
    )
    if not planta:
        raise ValueError("Planta não encontrada")

    especie = db.query(Especie).filter(Especie.id_especie == planta.id_especie).first()
    if not especie:
        raise ValueError("Espécie não encontrada")

    sete_dias_atras = datetime.now(timezone.utc) - timedelta(days=7)

    ultima_leitura = (
        db.query(LeituraUmidade)
        .filter(LeituraUmidade.id_planta == planta_id)
        .order_by(LeituraUmidade.data_hora_leitura.desc())
        .first()
    )

    media_result = (
        db.query(func.avg(LeituraUmidade.valor_umidade))
        .filter(
            LeituraUmidade.id_planta == planta_id,
            LeituraUmidade.data_hora_leitura >= sete_dias_atras,
        )
        .scalar()
    )

    total_irrigacoes = (
        db.query(func.count(HistoricoCuidado.id_historico))
        .filter(
            HistoricoCuidado.id_planta == planta_id,
            HistoricoCuidado.tipo_evento.like("%irrigacao%"),
            HistoricoCuidado.data_hora_evento >= sete_dias_atras,
        )
        .scalar()
    ) or 0

    ultima_irrigacao_obj = (
        db.query(HistoricoCuidado)
        .filter(
            HistoricoCuidado.id_planta == planta_id,
            HistoricoCuidado.tipo_evento.like("%irrigacao%"),
        )
        .order_by(HistoricoCuidado.data_hora_evento.desc())
        .first()
    )

    resultado = gerar_cronograma_ia(
        nome_especie=especie.nome_comum,
        nome_cientifico=especie.nome_cientifico,
        necessidade_luz=especie.necessidade_luz,
        observacoes_cuidado=especie.observacoes_cuidado,
        ambiente=planta.ambiente,
        porte=planta.porte,
        localizacao=planta.localizacao_descricao,
        umidade_atual=float(ultima_leitura.valor_umidade) if ultima_leitura else None,
        media_umidade_7d=float(media_result) if media_result else None,
        total_irrigacoes_7d=total_irrigacoes,
        ultima_irrigacao=(
            ultima_irrigacao_obj.data_hora_evento.isoformat()
            if ultima_irrigacao_obj
            else None
        ),
    )

    db.query(CronogramaCuidado).filter(
        CronogramaCuidado.id_planta == planta_id,
        CronogramaCuidado.ativo.is_(True),
    ).update({"ativo": False})

    hoje = date.today()
    cronograma = CronogramaCuidado(
        id_planta=planta_id,
        periodo_inicio=hoje,
        periodo_fim=hoje + timedelta(days=7),
        descricao_resumida=(
            f"Irrigar {resultado['frequencia_semanal']}x/semana às {resultado['horario_sugerido']}"
        ),
        ativo=True,
    )
    db.add(cronograma)
    db.flush()

    hora, minuto = map(int, resultado["horario_sugerido"].split(":"))
    itens = []
    for nome_dia in resultado["dias_sugeridos"]:
        data_dia = _proximo_dia_semana(nome_dia, hoje)
        data_prevista = datetime.combine(data_dia, time(hora, minuto), tzinfo=timezone.utc)
        item = ItemCronograma(
            id_cronograma=cronograma.id_cronograma,
            tipo_cuidado="irrigacao",
            descricao=resultado["observacoes"],
            data_prevista=data_prevista,
            status_execucao="pendente",
            origem_item="ia",
        )
        db.add(item)
        itens.append(item)

    recomendacao = RecomendacaoIA(
        id_planta=planta_id,
        tipo_recomendacao="cronograma_irrigacao",
        descricao_recomendacao=resultado["observacoes"],
        nivel_prioridade=resultado["nivel_prioridade"],
        status_recomendacao="ativa",
        justificativa=resultado["justificativa"],
    )
    db.add(recomendacao)
    db.commit()
    db.refresh(cronograma)
    for item in itens:
        db.refresh(item)

    return {
        "id_cronograma": cronograma.id_cronograma,
        "id_planta": planta_id,
        "frequencia_semanal": resultado["frequencia_semanal"],
        "dias_sugeridos": resultado["dias_sugeridos"],
        "horario_sugerido": resultado["horario_sugerido"],
        "nivel_prioridade": resultado["nivel_prioridade"],
        "observacoes": resultado["observacoes"],
        "justificativa": resultado["justificativa"],
        "periodo_inicio": cronograma.periodo_inicio,
        "periodo_fim": cronograma.periodo_fim,
        "itens": itens,
    }
