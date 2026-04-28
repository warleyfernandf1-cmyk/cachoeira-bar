from fastapi import APIRouter, HTTPException, Depends
from models.schemas import UsuarioCreate, UsuarioUpdate
from models.database import acquire
from services.auth_service import hash_password
from dependencies import require_perfil

router = APIRouter(prefix="/usuarios", tags=["usuarios"])

_admin = Depends(require_perfil("administrador"))


@router.get("", dependencies=[_admin])
async def listar():
    async with acquire() as conn:
        rows = await conn.fetch(
            "SELECT id, nome, email, perfil, ativo, created_at FROM usuarios ORDER BY nome"
        )
    return [dict(r) for r in rows]


@router.post("", dependencies=[_admin], status_code=201)
async def criar(body: UsuarioCreate):
    async with acquire() as conn:
        existe = await conn.fetchval(
            "SELECT id FROM usuarios WHERE email = $1", body.email.lower().strip()
        )
        if existe:
            raise HTTPException(status_code=409, detail="Email já cadastrado")
        row = await conn.fetchrow(
            """INSERT INTO usuarios (nome, email, senha_hash, perfil)
               VALUES ($1,$2,$3,$4) RETURNING id, nome, email, perfil, ativo, created_at""",
            body.nome.strip(), body.email.lower().strip(),
            hash_password(body.senha), body.perfil,
        )
    return dict(row)


@router.put("/{usuario_id}", dependencies=[_admin])
async def atualizar(usuario_id: int, body: UsuarioUpdate):
    async with acquire() as conn:
        user = await conn.fetchrow("SELECT id FROM usuarios WHERE id = $1", usuario_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        updates = body.model_dump(exclude_none=True)
        if "senha" in updates:
            updates["senha_hash"] = hash_password(updates.pop("senha"))
        if "email" in updates:
            updates["email"] = updates["email"].lower().strip()
        if not updates:
            return {"ok": True}

        sets = ", ".join(f"{k} = ${i+2}" for i, k in enumerate(updates))
        row = await conn.fetchrow(
            f"UPDATE usuarios SET {sets} WHERE id = $1 RETURNING id, nome, email, perfil, ativo",
            usuario_id, *list(updates.values()),
        )
    return dict(row)


@router.delete("/{usuario_id}", dependencies=[_admin])
async def desativar(usuario_id: int):
    async with acquire() as conn:
        row = await conn.fetchrow(
            "UPDATE usuarios SET ativo = FALSE WHERE id = $1 RETURNING id", usuario_id
        )
        if not row:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return {"ok": True}
