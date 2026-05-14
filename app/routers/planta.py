from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.planta import PlantaCreate, PlantaResponse, PlantaUpdate
from app.crud import planta as crud
from app.core.deps import get_current_user

router = APIRouter(prefix="/plantas", tags=["Plantas"])


# 🔹 POST - Criar planta
@router.post("/", response_model=PlantaResponse, status_code=status.HTTP_201_CREATED)
def criar_planta(
    data: PlantaCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return crud.create_planta(db, data, user["id_usuario"])


# 🔹 GET - Listar plantas do usuário
@router.get("/", response_model=list[PlantaResponse])
def listar_plantas(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return crud.get_plantas(db, user["id_usuario"])


# 🔹 GET - Detalhar planta
@router.get("/{planta_id}", response_model=PlantaResponse)
def detalhar_planta(
    planta_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    planta = crud.get_planta(db, planta_id, user["id_usuario"])

    if not planta:
        raise HTTPException(status_code=404, detail="Planta não encontrada")

    return planta


# 🔹 PUT/PATCH - Atualizar
@router.put("/{planta_id}", response_model=PlantaResponse)
def atualizar_planta(
    planta_id: int,
    data: PlantaUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    planta = crud.get_planta(db, planta_id, user["id_usuario"])

    if not planta:
        raise HTTPException(status_code=404, detail="Planta não encontrada")

    return crud.update_planta(db, planta, data)


# 🔹 DELETE
@router.delete("/{planta_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_planta(
    planta_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    planta = crud.get_planta(db, planta_id, user["id_usuario"])

    if not planta:
        raise HTTPException(status_code=404, detail="Planta não encontrada")

    crud.delete_planta(db, planta)