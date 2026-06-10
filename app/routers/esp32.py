from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_device
from app.db.session import get_db
from app.models.comando_irrigacao import ComandoIrrigacao
from app.models.evento_irrigacao import EventoIrrigacao
from app.models.leitura_sensor import LeituraSensor
from app.models.planta import Planta
from app.schemas.esp32 import (
    ComandoESP32Response,
    ComandoIrrigacaoCreate,
    ComandoIrrigacaoResponse,
    EventoIrrigacaoCreate,
    EventoIrrigacaoResponse,
    IrrigarResponse,
    LeituraSensorCreate,
    LeituraSensorResponse,
    StatusPlantaResponse,
    UltimaIrrigacaoStatus,
    UltimaLeituraStatus,
)

router = APIRouter(tags=["IoT"])


def _get_planta_or_404(planta_id: int, db: Session) -> Planta:
    planta = db.execute(
        select(Planta).where(Planta.id_planta == planta_id)
    ).scalar_one_or_none()
    if not planta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Planta não encontrada")
    return planta


@router.post("/leituras", response_model=LeituraSensorResponse, status_code=status.HTTP_201_CREATED)
def registrar_leitura(
    data: LeituraSensorCreate,
    db: Session = Depends(get_db),
    _=Depends(get_device),
):
    _get_planta_or_404(data.planta_id, db)
    leitura = LeituraSensor(
        id_planta=data.planta_id,
        umidade_percentual=data.umidade_percentual,
        adc_bruto=data.adc_bruto,
    )
    db.add(leitura)
    db.commit()
    db.refresh(leitura)
    return leitura


@router.get("/leituras/{planta_id}", response_model=list[LeituraSensorResponse])
def listar_leituras(
    planta_id: int,
    limit: int = Query(default=100, le=500),
    offset: int = Query(default=0),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    _get_planta_or_404(planta_id, db)
    rows = db.execute(
        select(LeituraSensor)
        .where(LeituraSensor.id_planta == planta_id)
        .order_by(LeituraSensor.timestamp.desc())
        .limit(limit)
        .offset(offset)
    ).scalars().all()
    return rows


@router.post("/irrigacao", response_model=EventoIrrigacaoResponse, status_code=status.HTTP_201_CREATED)
def registrar_evento_irrigacao(
    data: EventoIrrigacaoCreate,
    db: Session = Depends(get_db),
    _=Depends(get_device),
):
    _get_planta_or_404(data.planta_id, db)
    evento = EventoIrrigacao(
        id_planta=data.planta_id,
        duracao_segundos=data.duracao_segundos,
    )
    db.add(evento)
    db.commit()
    db.refresh(evento)
    return evento


@router.get("/irrigacao/{planta_id}", response_model=list[EventoIrrigacaoResponse])
def listar_eventos_irrigacao(
    planta_id: int,
    limit: int = Query(default=100, le=500),
    offset: int = Query(default=0),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    _get_planta_or_404(planta_id, db)
    rows = db.execute(
        select(EventoIrrigacao)
        .where(EventoIrrigacao.id_planta == planta_id)
        .order_by(EventoIrrigacao.timestamp.desc())
        .limit(limit)
        .offset(offset)
    ).scalars().all()
    return rows


@router.post("/irrigar", response_model=IrrigarResponse)
def solicitar_irrigacao(
    data: ComandoIrrigacaoCreate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    _get_planta_or_404(data.planta_id, db)

    existente = db.execute(
        select(ComandoIrrigacao).where(
            ComandoIrrigacao.id_planta == data.planta_id,
            ComandoIrrigacao.pendente.is_(True),
        )
    ).scalar_one_or_none()

    if existente:
        return IrrigarResponse(
            mensagem="Já existe um comando pendente para esta planta",
            comando=ComandoIrrigacaoResponse.model_validate(existente),
        )

    comando = ComandoIrrigacao(id_planta=data.planta_id, pendente=True)
    db.add(comando)
    db.commit()
    db.refresh(comando)
    return IrrigarResponse(
        mensagem="Comando de irrigação criado com sucesso",
        comando=ComandoIrrigacaoResponse.model_validate(comando),
    )


@router.get("/comando/{planta_id}", response_model=ComandoESP32Response)
def consultar_comando(
    planta_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_device),
):
    comando = db.execute(
        select(ComandoIrrigacao)
        .where(
            ComandoIrrigacao.id_planta == planta_id,
            ComandoIrrigacao.pendente.is_(True),
        )
        .order_by(ComandoIrrigacao.criado_em.desc())
        .limit(1)
    ).scalar_one_or_none()

    if not comando:
        return ComandoESP32Response(irrigar=False)

    comando.pendente = False
    db.commit()
    return ComandoESP32Response(irrigar=True)


@router.get("/status/{planta_id}", response_model=StatusPlantaResponse)
def status_planta(
    planta_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    _get_planta_or_404(planta_id, db)

    ultima_leitura = db.execute(
        select(LeituraSensor)
        .where(LeituraSensor.id_planta == planta_id)
        .order_by(LeituraSensor.timestamp.desc())
        .limit(1)
    ).scalar_one_or_none()

    ultimo_evento = db.execute(
        select(EventoIrrigacao)
        .where(EventoIrrigacao.id_planta == planta_id)
        .order_by(EventoIrrigacao.timestamp.desc())
        .limit(1)
    ).scalar_one_or_none()

    tem_pendente = db.execute(
        select(ComandoIrrigacao)
        .where(
            ComandoIrrigacao.id_planta == planta_id,
            ComandoIrrigacao.pendente.is_(True),
        )
        .limit(1)
    ).scalar_one_or_none()

    # Firmware envia leitura a cada 30s; 90s = 3 ciclos sem resposta → offline
    _OFFLINE_THRESHOLD_SECONDS = 90
    dispositivo_online = False
    if ultima_leitura is not None:
        agora = datetime.now(timezone.utc)
        ultima_ts = ultima_leitura.timestamp
        if ultima_ts.tzinfo is None:
            ultima_ts = ultima_ts.replace(tzinfo=timezone.utc)
        dispositivo_online = (agora - ultima_ts).total_seconds() <= _OFFLINE_THRESHOLD_SECONDS

    return StatusPlantaResponse(
        ultima_leitura=UltimaLeituraStatus.model_validate(ultima_leitura) if ultima_leitura else None,
        ultimo_evento_irrigacao=UltimaIrrigacaoStatus.model_validate(ultimo_evento) if ultimo_evento else None,
        tem_comando_pendente=tem_pendente is not None,
        dispositivo_online=dispositivo_online,
    )
