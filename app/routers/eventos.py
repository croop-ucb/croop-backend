from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import get_current_user
from app.services.evento_notificacao_service import processar_evento_sensor

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
        user.id_usuario,
        planta_id,
        umidade,
        sensor_ok
    )

    return {"message": "evento processado"}