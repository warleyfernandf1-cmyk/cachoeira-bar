from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from models.schemas import ProdutoCreate, ProdutoUpdate
from models.database import acquire
from dependencies import get_current_user, require_perfil

router = APIRouter(prefix="/produtos", tags=["produtos"])

_admin = Depends(require_perfil("administrador"))


@router.get("")
async def listar(
    categoria: Optional[str] = Query(None),
    setor:     Optional[str] = Query(None),
    _: dict = Depends(get_current_user),
):
    query  = "SELECT * FROM produtos WHERE ativo = TRUE"
    params = []
    if categoria:
        params.append(categoria)
        query += f" AND categoria = ${len(params)}"
    if setor:
        params.append(setor)
        query += f" AND setor = ${len(params)}"
    query += " ORDER BY categoria, nome"

    async with acquire() as conn:
        rows = await conn.fetch(query, *params)
    return [dict(r) for r in rows]


@router.post("", dependencies=[_admin], status_code=201)
async def criar(body: ProdutoCreate):
    async with acquire() as conn:
        row = await conn.fetchrow(
            """INSERT INTO produtos (nome, categoria, preco, unidade, tempo_preparo, setor)
               VALUES ($1,$2,$3,$4,$5,$6) RETURNING *""",
            body.nome.strip(), body.categoria, body.preco,
            body.unidade, body.tempo_preparo, body.setor,
        )
    return dict(row)


@router.put("/{produto_id}", dependencies=[_admin])
async def atualizar(produto_id: int, body: ProdutoUpdate):
    updates = body.model_dump(exclude_none=True)
    if not updates:
        return {"ok": True}

    async with acquire() as conn:
        prod = await conn.fetchrow("SELECT id FROM produtos WHERE id = $1", produto_id)
        if not prod:
            raise HTTPException(status_code=404, detail="Produto não encontrado")

        sets = ", ".join(f"{k} = ${i+2}" for i, k in enumerate(updates))
        row = await conn.fetchrow(
            f"UPDATE produtos SET {sets} WHERE id = $1 RETURNING *",
            produto_id, *list(updates.values()),
        )
    return dict(row)


@router.delete("/{produto_id}", dependencies=[_admin])
async def desativar(produto_id: int):
    async with acquire() as conn:
        row = await conn.fetchrow(
            "UPDATE produtos SET ativo = FALSE WHERE id = $1 RETURNING id", produto_id
        )
        if not row:
            raise HTTPException(status_code=404, detail="Produto não encontrado")
    return {"ok": True}
