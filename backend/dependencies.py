from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from services.auth_service import decode_token

_bearer = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> dict:
    try:
        payload = decode_token(credentials.credentials)
        return {
            "id":     int(payload["sub"]),
            "email":  payload["email"],
            "perfil": payload["perfil"],
        }
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")


def require_perfil(*perfis: str):
    """Dependência de RBAC — bloqueia perfis não autorizados."""
    async def dependency(current_user: dict = Depends(get_current_user)) -> dict:
        if current_user["perfil"] not in perfis:
            raise HTTPException(status_code=403, detail="Acesso negado para este perfil")
        return current_user
    return dependency
