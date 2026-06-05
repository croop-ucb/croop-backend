from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.schemas.cronograma import CronogramaResponse
from app.services.cronograma_service import gerar_e_persistir_cronograma

router = APIRouter(prefix="/plantas", tags=["Cronograma"])


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
