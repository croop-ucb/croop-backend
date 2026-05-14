from sqlalchemy.orm import Session
from app.models.planta import Planta
from app.schemas.planta import PlantaCreate, PlantaUpdate


def create_planta(db: Session, data: PlantaCreate, user_id: int):
    planta = Planta(
        **data.model_dump(),
        id_usuario=user_id
    )
    db.add(planta)
    db.commit()
    db.refresh(planta)
    return planta


def get_plantas(db: Session, user_id: int):
    return db.query(Planta).filter(Planta.id_usuario == user_id).all()


def get_planta(db: Session, planta_id: int, user_id: int):
    return db.query(Planta).filter(
        Planta.id_planta == planta_id,
        Planta.id_usuario == user_id
    ).first()


def update_planta(db: Session, planta: Planta, data: PlantaUpdate):
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(planta, field, value)

    db.commit()
    db.refresh(planta)
    return planta


def delete_planta(db: Session, planta: Planta):
    db.delete(planta)
    db.commit()