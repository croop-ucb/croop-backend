from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.planta import PlantaCreate, PlantaResponse, PlantaUpdate
from app.crud import planta as crud
from app.core.deps import get_current_user

from app.models.planta import Planta
from app.models.vinculo_planta_dispositivo import VinculoPlantaDispositivo
from app.models.leitura_umidade import LeituraUmidade
from app.models.historico_cuidado import HistoricoCuidado
from app.models.especie import Especie
from app.services.cronograma_service import gerar_e_persistir_cronograma

router = APIRouter(prefix="/plantas", tags=["Plantas"])


# 🔹 POST - Criar planta
@router.post("/", response_model=PlantaResponse, status_code=status.HTTP_201_CREATED)
def criar_planta(
    data: PlantaCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    planta = crud.create_planta(db, data, user["id_usuario"])
    try:
        gerar_e_persistir_cronograma(db, planta.id_planta, user["id_usuario"])
    except Exception:
        pass
    return planta


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

@router.post("/{planta_id}/irrigar")
def irrigar_planta(
    planta_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    # Buscar planta do usuário
    planta = (
        db.query(Planta)
        .filter(
            Planta.id_planta == planta_id,
            Planta.id_usuario == user["id_usuario"]
        )
        .first()
    )

    if not planta:
        raise HTTPException(
            status_code=404,
            detail="Planta não encontrada"
        )

    # Verificar vínculo ativo com dispositivo
    vinculo = (
        db.query(VinculoPlantaDispositivo)
        .filter(
            VinculoPlantaDispositivo.id_planta == planta_id,
            VinculoPlantaDispositivo.ativo.is_(True)
        )
        .first()
    )

    if not vinculo:
        raise HTTPException(
            status_code=400,
            detail="Planta não possui dispositivo vinculado"
        )

    # Buscar última leitura de umidade
    leitura = (
        db.query(LeituraUmidade)
        .filter(LeituraUmidade.id_planta == planta_id)
        .order_by(LeituraUmidade.data_hora_leitura.desc())
        .first()
    )

    if not leitura:
        raise HTTPException(
            status_code=400,
            detail="Planta não possui leitura de umidade"
        )

    # Buscar espécie da planta
    especie = (
        db.query(Especie)
        .filter(Especie.id_especie == planta.id_especie)
        .first()
    )

    limite_umidade = (
        float(planta.faixa_umidade_max) if planta.faixa_umidade_max is not None
        else (float(especie.faixa_umidade_max) if especie and especie.faixa_umidade_max is not None else 80)
    )

    # Bloqueia irrigação se estiver acima do limite
    if (
        limite_umidade is not None
        and leitura.valor_umidade >= limite_umidade
    ):
        historico = HistoricoCuidado(
            id_planta=planta.id_planta,
            tipo_evento="irrigacao_manual",
            descricao_evento="Tentativa bloqueada por umidade alta",
            origem_evento="manual"
        )

        db.add(historico)
        db.commit()

        raise HTTPException(
            status_code=409,
            detail="Umidade acima do limite permitido"
        )

    # Simulação de envio para dispositivo IoT
    sucesso_dispositivo = True

    if not sucesso_dispositivo:
        historico = HistoricoCuidado(
            id_planta=planta.id_planta,
            tipo_evento="irrigacao_manual",
            descricao_evento="Falha na comunicação com dispositivo",
            origem_evento="manual"
        )

        db.add(historico)
        db.commit()

        raise HTTPException(
            status_code=503,
            detail="Falha na comunicação com dispositivo"
        )

    # Registrar sucesso no histórico
    historico = HistoricoCuidado(
        id_planta=planta.id_planta,
        tipo_evento="irrigacao_manual",
        descricao_evento="Irrigação manual executada com sucesso",
        origem_evento="manual"
    )

    db.add(historico)
    db.commit()

    return {
        "mensagem": "Irrigação manual enviada com sucesso"
    }
