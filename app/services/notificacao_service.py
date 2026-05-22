from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.models.notificacao import Notificacao

INTERVALO_MINUTOS = 30


def pode_enviar_notificacao(
    db: Session,
    user_id: int,
    tipo: str,
    planta_id: int | None = None
):
    limite = datetime.utcnow() - timedelta(minutes=INTERVALO_MINUTOS)

    query = db.query(Notificacao).filter(
        Notificacao.id_usuario == user_id,
        Notificacao.tipo_notificacao == tipo,
        Notificacao.data_envio >= limite
    )

    if planta_id:
        query = query.filter(Notificacao.id_planta == planta_id)

    notificacao_recente = query.first()

    return notificacao_recente is None


def gerar_notificacao(
    db: Session,
    user_id: int,
    tipo: str,
    titulo: str,
    mensagem: str,
    planta_id: int | None = None
):
    # RN-011 → evitar duplicação
    if not pode_enviar_notificacao(db, user_id, tipo, planta_id):
        return None

    notificacao = Notificacao(
        id_usuario=user_id,
        id_planta=planta_id,
        tipo_notificacao=tipo,
        titulo=titulo,
        mensagem=mensagem,
        canal_envio="sistema"
    )

    db.add(notificacao)
    db.commit()
    db.refresh(notificacao)

    return notificacao