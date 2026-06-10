from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.security import SECRET_KEY, ALGORITHM
from app.db.session import get_db
from app.models.dispositivo_iot import DispositivoIot
from app.models.planta import Planta
from app.models.vinculo_planta_dispositivo import VinculoPlantaDispositivo
from app.schemas.dispositivo import (
    AtivarDispositivoRequest,
    AtivarDispositivoResponse,
    GerarTokenRequest,
    GerarTokenResponse,
)

router = APIRouter(prefix="/dispositivos", tags=["Dispositivos"])

_PAIRING_TOKEN_EXPIRE_MINUTES = 10
_PAIRING_TOKEN_SUB = "vinculacao"


@router.post("/gerar-token", response_model=GerarTokenResponse)
def gerar_token(
    data: GerarTokenRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    planta = db.execute(
        select(Planta).where(
            Planta.id_planta == data.planta_id,
            Planta.id_usuario == user["id_usuario"],
        )
    ).scalar_one_or_none()
    if not planta:
        raise HTTPException(status_code=404, detail="Planta não encontrada")

    expire = datetime.now(timezone.utc) + timedelta(minutes=_PAIRING_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": _PAIRING_TOKEN_SUB,
        "planta_id": data.planta_id,
        "user_id": user["id_usuario"],
        "exp": expire,
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return GerarTokenResponse(token=token, expires_in=_PAIRING_TOKEN_EXPIRE_MINUTES * 60)


@router.post("/ativar", response_model=AtivarDispositivoResponse)
def ativar_dispositivo(
    data: AtivarDispositivoRequest,
    db: Session = Depends(get_db),
):
    try:
        payload = jwt.decode(data.token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("sub") != _PAIRING_TOKEN_SUB:
            raise HTTPException(status_code=400, detail="Token inválido")
        planta_id: int = payload["planta_id"]
        user_id: int = payload["user_id"]
    except JWTError:
        raise HTTPException(status_code=400, detail="Token inválido ou expirado")

    agora = datetime.now(timezone.utc)

    dispositivo = db.execute(
        select(DispositivoIot).where(DispositivoIot.codigo_serie == data.codigo_serie)
    ).scalar_one_or_none()

    if not dispositivo:
        dispositivo = DispositivoIot(
            id_usuario=user_id,
            codigo_serie=data.codigo_serie,
            status_dispositivo="ativo",
            data_ativacao=agora,
            ultima_comunicacao=agora,
        )
        db.add(dispositivo)
        db.flush()
    else:
        dispositivo.id_usuario = user_id
        dispositivo.status_dispositivo = "ativo"
        dispositivo.ultima_comunicacao = agora

    vinculos_ativos = db.execute(
        select(VinculoPlantaDispositivo).where(
            VinculoPlantaDispositivo.id_dispositivo == dispositivo.id_dispositivo,
            VinculoPlantaDispositivo.ativo.is_(True),
        )
    ).scalars().all()
    for v in vinculos_ativos:
        v.ativo = False
        v.data_fim = agora

    vinculo = VinculoPlantaDispositivo(
        id_planta=planta_id,
        id_dispositivo=dispositivo.id_dispositivo,
        ativo=True,
    )
    db.add(vinculo)
    db.commit()

    return AtivarDispositivoResponse(planta_id=planta_id)
