from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import SECRET_KEY, ALGORITHM
from app.db.session import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/usuarios/login")


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado"
        )


def get_device(x_device_key: str = Header(...), db: Session = Depends(get_db)):
    from app.models.dispositivo_iot import DispositivoIot
    dispositivo = db.execute(
        select(DispositivoIot).where(DispositivoIot.codigo_serie == x_device_key)
    ).scalar_one_or_none()
    if not dispositivo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Dispositivo não autorizado"
        )
    return dispositivo