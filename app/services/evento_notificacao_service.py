from sqlalchemy.orm import Session
from app.services.notificacao_service import gerar_notificacao


def processar_evento_sensor(
    db: Session,
    user_id: int,
    planta_id: int,
    umidade: float | None,
    sensor_ok: bool
):
    """
    UC-009: motor de eventos automáticos
    """

    # ❌ Falha de sensor
    if not sensor_ok:
        gerar_notificacao(
            db,
            user_id,
            "falha_sensor",
            "Falha no sensor",
            "Não foi possível ler os dados do sensor ⚠️",
            planta_id
        )
        return

    # 🌱 Precisa irrigar
    if umidade is not None and umidade < 30:
        gerar_notificacao(
            db,
            user_id,
            "irrigacao",
            "Hora de regar",
            "Sua planta precisa de água 🌱",
            planta_id
        )

    # 💧 Excesso de água
    if umidade is not None and umidade > 80:
        gerar_notificacao(
            db,
            user_id,
            "excesso_agua",
            "Excesso de água",
            "Solo muito úmido 💧 reduza irrigação",
            planta_id
        )