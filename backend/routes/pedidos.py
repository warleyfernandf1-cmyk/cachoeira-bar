from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from models.schemas import PedidoCreate
from models.database import acquire
from services.pedido_service import criar_pedido, get_pedido
from services.impressao_service import imprimir_pedido
from dependencies import require_perfil

router = APIRouter(prefix="/pedidos", tags=["pedidos"])

_recepcao = Depends(require_perfil("administrador", "recepcionista"))


@router.post("", dependencies=[_recepcao], status_code=201)
async def novo_pedido(body: PedidoCreate):
    async with acquire() as conn:
        try:
            pedido = await criar_pedido(
                conn, body.mesa_id, [i.model_dump() for i in body.itens], body.observacao
            )
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))

    imprimir_pedido(pedido)  # Supabase Realtime notifica o frontend automaticamente
    return pedido


@router.get("")
async def listar(
    status: Optional[str] = Query(None),
    _: dict = Depends(require_perfil("administrador", "recepcionista", "garcom")),
):
    query  = "SELECT p.*, m.numero AS mesa_numero FROM pedidos p JOIN mesas m ON m.id = p.mesa_id"
    params = []
    if status:
        params.append(status)
        query += f" WHERE p.status = ${len(params)}"
    query += " ORDER BY p.created_at DESC"

    async with acquire() as conn:
        rows = await conn.fetch(query, *params)

    return [
        {
            "id":           r["id"],
            "codigo":       r["codigo"],
            "mesa":         r["mesa_numero"],
            "status":       r["status"],
            "valor_total":  float(r["valor_total"]),
            "tempo_estimado": r["tempo_estimado"],
            "created_at":   r["created_at"].isoformat() if r["created_at"] else None,
            "pronto_at":    r["pronto_at"].isoformat()  if r["pronto_at"]  else None,
        }
        for r in rows
    ]


@router.get("/{pedido_id}")
async def detalhar(
    pedido_id: int,
    _: dict = Depends(require_perfil("administrador", "recepcionista", "cozinheiro", "churrasqueiro", "garcom")),
):
    async with acquire() as conn:
        pedido = await get_pedido(conn, pedido_id)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return pedido
