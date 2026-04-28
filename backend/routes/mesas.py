from fastapi import APIRouter, HTTPException, Depends
from models.schemas import MesaCreate
from models.database import acquire
from dependencies import get_current_user, require_perfil

router = APIRouter(prefix="/mesas", tags=["mesas"])

_admin = Depends(require_perfil("administrador"))


@router.get("")
async def listar(_: dict = Depends(get_current_user)):
    async with acquire() as conn:
        rows = await conn.fetch("SELECT * FROM mesas ORDER BY numero")
    return [dict(r) for r in rows]


@router.post("", dependencies=[_admin], status_code=201)
async def criar(body: MesaCreate):
    numero = body.numero.upper().strip()
    async with acquire() as conn:
        existe = await conn.fetchval("SELECT id FROM mesas WHERE numero = $1", numero)
        if existe:
            raise HTTPException(status_code=409, detail="Mesa já cadastrada")
        row = await conn.fetchrow(
            "INSERT INTO mesas (numero) VALUES ($1) RETURNING *", numero
        )
    return dict(row)


@router.put("/{mesa_id}/status", dependencies=[_admin])
async def atualizar_status(mesa_id: int, status: str):
    if status not in ("livre", "ocupada"):
        raise HTTPException(status_code=422, detail="Status inválido")
    async with acquire() as conn:
        row = await conn.fetchrow(
            "UPDATE mesas SET status=$1 WHERE id=$2 RETURNING *", status, mesa_id
        )
        if not row:
            raise HTTPException(status_code=404, detail="Mesa não encontrada")
    return dict(row)


@router.delete("/{mesa_id}", dependencies=[_admin])
async def deletar(mesa_id: int):
    async with acquire() as conn:
        row = await conn.fetchrow("DELETE FROM mesas WHERE id=$1 RETURNING id", mesa_id)
        if not row:
            raise HTTPException(status_code=404, detail="Mesa não encontrada")
    return {"ok": True}
