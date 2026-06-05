from fastapi import APIRouter, Depends, HTTPException
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


@router.patch("/{notificacao_id}/ler", status_code=204)
def marcar_como_lida(
    notificacao_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    notificacao = db.query(Notificacao).filter(
        Notificacao.id_notificacao == notificacao_id,
        Notificacao.id_usuario == user["id_usuario"],
    ).first()
    if not notificacao:
        raise HTTPException(status_code=404, detail="Notificação não encontrada")
    notificacao.lida = True
    db.commit()