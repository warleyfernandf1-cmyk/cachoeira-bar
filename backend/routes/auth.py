from fastapi import APIRouter, HTTPException, Depends
from models.schemas import LoginRequest, TokenResponse
from models.database import acquire
from services.auth_service import verify_password, create_token, hash_password
from dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest):
    async with acquire() as conn:
        user = await conn.fetchrow(
            "SELECT * FROM usuarios WHERE email = $1 AND ativo = TRUE",
            body.email.lower().strip(),
        )
    if not user or not verify_password(body.senha, user["senha_hash"]):
        raise HTTPException(status_code=401, detail="Email ou senha incorretos")

    token = create_token(user["id"], user["email"], user["perfil"])
    return TokenResponse(access_token=token, perfil=user["perfil"], nome=user["nome"])


@router.post("/setup-admin")
async def setup_admin():
    """Cria o administrador inicial. Só funciona se nenhum admin existir."""
    async with acquire() as conn:
        count = await conn.fetchval(
            "SELECT COUNT(*) FROM usuarios WHERE perfil = 'administrador'"
        )
        if count > 0:
            raise HTTPException(status_code=403, detail="Administrador já existe")
        senha_hash = hash_password("Admin@123")
        await conn.execute(
            "INSERT INTO usuarios (nome, email, senha_hash, perfil) VALUES ($1,$2,$3,$4)",
            "Administrador", "admin@cachoeira.com", senha_hash, "administrador",
        )
    return {"mensagem": "Admin criado.", "email": "admin@cachoeira.com", "senha": "Admin@123"}


@router.get("/me")
async def me(current_user: dict = Depends(get_current_user)):
    return current_user
