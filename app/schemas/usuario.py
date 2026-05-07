import re
from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator, model_validator


class UsuarioCadastroRequest(BaseModel):
    nome: str
    cpf: str
    email: EmailStr
    senha: str
    confirmacao_senha: str

    @field_validator("senha")
    @classmethod
    def validar_senha(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Senha deve ter no mínimo 6 caracteres")
        if " " in v:
            raise ValueError("Senha não pode conter espaços")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Senha deve conter pelo menos uma letra maiúscula")
        if not re.search(r"[a-z]", v):
            raise ValueError("Senha deve conter pelo menos uma letra minúscula")
        if not re.search(r"\d", v):
            raise ValueError("Senha deve conter pelo menos um número")
        return v

    @model_validator(mode="after")
    def validar_confirmacao_e_igualdade_email(self) -> "UsuarioCadastroRequest":
        if self.senha != self.confirmacao_senha:
            raise ValueError("Confirmação de senha não corresponde")
        if self.senha.lower() == str(self.email).lower():
            raise ValueError("Senha não pode ser igual ao e-mail")
        return self


class UsuarioCadastroResponse(BaseModel):
    id_usuario: int
    nome: str
    email: str
    data_cadastro: datetime

    model_config = {"from_attributes": True}

class UsuarioLoginRequest(BaseModel):
    email: EmailStr
    senha: str

class TokenResponse(BaseModel):
  access_token: str
  token_type: str