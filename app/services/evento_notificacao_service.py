from sqlalchemy.orm import Session
from app.services.notificacao_service import gerar_notificacao


def processar_evento_sensor(
    db: Session,
    user_id: int,
    planta_id: int,
    umidade: float | None,
    sensor_ok: bool,
    umidade_min: float | None = None,
    umidade_max: float | None = None,
):
    """
    UC-009: motor de eventos automáticos.
    Thresholds de umidade só disparam se configurados na espécie da planta.
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

    if umidade is not None and umidade_min is not None:
        limiar_critico = umidade_min / 3

        # 🚨 Umidade crítica (abaixo de 1/3 do mínimo da espécie)
        if umidade < limiar_critico:
            gerar_notificacao(
                db,
                user_id,
                "umidade_critica",
                "Umidade crítica",
                f"Solo com apenas {umidade:.0f}% de umidade — regue imediatamente",
                planta_id
            )
        # 🌱 Precisa irrigar
        elif umidade < umidade_min:
            gerar_notificacao(
                db,
                user_id,
                "irrigacao",
                "Hora de regar",
                "Sua planta precisa de água 🌱",
                planta_id
            )

    # 💧 Excesso de água
    if umidade is not None and umidade_max is not None and umidade > umidade_max:
        gerar_notificacao(
            db,
            user_id,
            "excesso_agua",
            "Excesso de água",
            "Solo muito úmido 💧 reduza irrigação",
            planta_id
        )