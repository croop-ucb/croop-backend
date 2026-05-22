from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.especie import Especie
from app.schemas.especie import EspecieResponse
from app.core.deps import get_current_user

router = APIRouter(prefix="/especies", tags=["Espécies"])


@router.get("/", response_model=list[EspecieResponse])
def listar_especies(
    busca: str | None = Query(None, description="Filtra por nome comum ou científico"),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    query = db.query(Especie)
    if busca:
        termo = f"%{busca}%"
        query = query.filter(
            Especie.nome_comum.ilike(termo) | Especie.nome_cientifico.ilike(termo)
        )
    return query.order_by(Especie.nome_comum).all()
