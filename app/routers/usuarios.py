from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_senha
from app.db.session import get_db
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCadastroRequest, UsuarioCadastroResponse

router = APIRouter(prefix="/usuarios", tags=["Usuários"])


@router.post(
    "/cadastro",
    response_model=UsuarioCadastroResponse,
    status_code=status.HTTP_201_CREATED,
)
def cadastrar_usuario(dados: UsuarioCadastroRequest, db: Session = Depends(get_db)):
    if db.query(Usuario).filter(Usuario.email == dados.email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="E-mail já cadastrado",
        )

    usuario = Usuario(
        nome=dados.nome,
        cpf=dados.cpf,
        email=dados.email,
        senha_hash=hash_senha(dados.senha),
        status_conta="ativo",
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario
