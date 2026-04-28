from fastapi import APIRouter, HTTPException, Depends
from models.database import acquire
from services.pedido_service import get_pedido
from dependencies import require_perfil

router = APIRouter(prefix="/expedicao", tags=["expedicao"])

_garcom = Depends(require_perfil("administrador", "garcom"))


@router.get("")
async def listar_prontos(_: dict = Depends(require_perfil("administrador", "garcom"))):
    async with acquire() as conn:
        rows = await conn.fetch(
            """SELECT p.*, m.numero AS mesa_numero
               FROM pedidos p JOIN mesas m ON m.id = p.mesa_id
               WHERE p.status IN ('pronto','em_entrega')
               ORDER BY p.pronto_at ASC NULLS LAST, p.created_at ASC"""
        )
    return [
        {
            "id":          r["id"],
            "codigo":      r["codigo"],
            "mesa":        r["mesa_numero"],
            "status":      r["status"],
            "valor_total": float(r["valor_total"]),
            "created_at":  r["created_at"].isoformat() if r["created_at"] else None,
            "pronto_at":   r["pronto_at"].isoformat()  if r["pronto_at"]  else None,
            "entrega_at":  r["entrega_at"].isoformat() if r["entrega_at"] else None,
        }
        for r in rows
    ]


@router.put("/{pedido_id}/entregar", dependencies=[_garcom])
async def marcar_entrega(pedido_id: int):
    async with acquire() as conn:
        p = await conn.fetchrow("SELECT status FROM pedidos WHERE id=$1", pedido_id)
        if not p:
            raise HTTPException(status_code=404, detail="Pedido não encontrado")
        if p["status"] != "pronto":
            raise HTTPException(status_code=409, detail="Pedido não está com status PRONTO")
        await conn.execute(
            "UPDATE pedidos SET status='em_entrega', entrega_at=NOW() WHERE id=$1", pedido_id
        )
        return await get_pedido(conn, pedido_id)


@router.put("/{pedido_id}/finalizar", dependencies=[_garcom])
async def finalizar(pedido_id: int):
    async with acquire() as conn:
        p = await conn.fetchrow("SELECT status, mesa_id FROM pedidos WHERE id=$1", pedido_id)
        if not p:
            raise HTTPException(status_code=404, detail="Pedido não encontrado")
        if p["status"] not in ("em_entrega", "pronto"):
            raise HTTPException(status_code=409, detail="Pedido não está em entrega")

        async with conn.transaction():
            await conn.execute(
                "UPDATE pedidos SET status='finalizado', finalizado_at=NOW() WHERE id=$1", pedido_id
            )
            ativos = await conn.fetchval(
                """SELECT COUNT(*) FROM pedidos
                   WHERE mesa_id=$1 AND status NOT IN ('finalizado') AND id!=$2""",
                p["mesa_id"], pedido_id,
            )
            if ativos == 0:
                await conn.execute(
                    "UPDATE mesas SET status='livre' WHERE id=$1", p["mesa_id"]
                )

        return await get_pedido(conn, pedido_id)
