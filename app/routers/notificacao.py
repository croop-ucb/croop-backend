from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.notificacao import NotificacaoResponse
from app.models.notificacao import Notificacao
from app.core.deps import get_current_user

router = APIRouter(prefix="/notificacoes", tags=["Notificações"])


@router.get("/", response_model=list[NotificacaoResponse])
def listar_notificacoes(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return db.query(Notificacao).filter(
        Notificacao.id_usuario == user["id_usuario"]
    ).order_by(Notificacao.data_envio.desc()).all()