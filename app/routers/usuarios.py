from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_senha
from app.db.session import get_db
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCadastroRequest, UsuarioCadastroResponse
from app.schemas.usuario import UsuarioLoginRequest
from app.core.security import verificar_senha, criar_token
from app.schemas.usuario import TokenResponse
from app.core.deps import get_current_user

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

@router.post("/login", response_model=TokenResponse)
def login(dados: UsuarioLoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == dados.email).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas"
        )

    if not verificar_senha(dados.senha, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas"
        )

    token = criar_token({"sub": usuario.email, "id_usuario": usuario.id_usuario})

    return {
        "access_token": token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=UsuarioCadastroResponse)
def get_me(db: Session = Depends(get_db), user=Depends(get_current_user)):
    usuario = db.query(Usuario).filter(
        Usuario.id_usuario == user["id_usuario"]
    ).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario

@router.get("/protegido")
def rota_protegida(user=Depends(get_current_user)):
    return {"mensagem": "Você está autenticado!", "user": user}
