from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import get_current_user
from app.services.evento_notificacao_service import processar_evento_sensor
from app.services.cronograma_service import deve_regenerar, gerar_e_persistir_cronograma

router = APIRouter(prefix="/eventos", tags=["Eventos"])


@router.post("/sensor")
def evento_sensor(
    planta_id: int,
    umidade: float | None = None,
    sensor_ok: bool = True,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    processar_evento_sensor(
        db,
        user["id_usuario"],
        planta_id,
        umidade,
        sensor_ok
    )

    try:
        if deve_regenerar(db, planta_id):
            gerar_e_persistir_cronograma(db, planta_id, user["id_usuario"])
    except Exception:
        pass

    return {"message": "evento processado"}