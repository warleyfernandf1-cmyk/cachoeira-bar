from fastapi import APIRouter, HTTPException, Depends
from models.database import acquire
from services.pedido_service import get_pedido
from dependencies import require_perfil

router = APIRouter(prefix="/producao", tags=["producao"])

_PERFIL_SETORES = {
    "cozinheiro":    ["balcao_01", "balcao_02", "balcao_03"],
    "churrasqueiro": ["churrasqueira"],
    "administrador": ["balcao_01", "balcao_02", "balcao_03", "churrasqueira"],
}


def _check_setor(perfil: str, setor: str):
    if setor not in _PERFIL_SETORES.get(perfil, []):
        raise HTTPException(status_code=403, detail=f"Perfil '{perfil}' não acessa setor '{setor}'")


@router.get("/{setor}")
async def pedidos_do_setor(
    setor: str,
    current_user: dict = Depends(require_perfil("administrador", "cozinheiro", "churrasqueiro")),
):
    _check_setor(current_user["perfil"], setor)

    async with acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT ps.id AS setor_id, ps.status AS setor_status,
                   p.id AS pedido_id, p.codigo, p.status,
                   p.tempo_estimado, p.created_at, m.numero AS mesa_numero
            FROM pedidos_setores ps
            JOIN pedidos p ON p.id = ps.pedido_id
            JOIN mesas   m ON m.id = p.mesa_id
            WHERE ps.setor = $1
              AND ps.status = 'pendente'
              AND p.status  = 'em_producao'
            ORDER BY p.created_at ASC
            """,
            setor,
        )

        result = []
        for r in rows:
            itens = await conn.fetch(
                """SELECT ip.quantidade, pr.nome AS produto_nome
                   FROM itens_pedido ip JOIN produtos pr ON pr.id = ip.produto_id
                   WHERE ip.pedido_id = $1 AND pr.setor = $2
                   ORDER BY pr.nome""",
                r["pedido_id"], setor,
            )
            result.append({
                "setor_id":       r["setor_id"],
                "setor_status":   r["setor_status"],
                "pedido_id":      r["pedido_id"],
                "codigo":         r["codigo"],
                "mesa":           r["mesa_numero"],
                "status":         r["status"],
                "tempo_estimado": r["tempo_estimado"],
                "created_at":     r["created_at"].isoformat(),
                "itens": [{"produto_nome": i["produto_nome"], "quantidade": i["quantidade"]} for i in itens],
            })

    return result


@router.put("/setor/{setor_id}/concluir")
async def concluir_setor(
    setor_id: int,
    current_user: dict = Depends(require_perfil("administrador", "cozinheiro", "churrasqueiro")),
):
    async with acquire() as conn:
        setor_rec = await conn.fetchrow(
            "SELECT * FROM pedidos_setores WHERE id = $1", setor_id
        )
        if not setor_rec:
            raise HTTPException(status_code=404, detail="Registro de setor não encontrado")

        _check_setor(current_user["perfil"], setor_rec["setor"])

        if setor_rec["status"] == "concluido":
            raise HTTPException(status_code=409, detail="Setor já foi concluído")

        async with conn.transaction():
            await conn.execute(
                "UPDATE pedidos_setores SET status='concluido', concluido_at=NOW() WHERE id=$1",
                setor_id,
            )
            pendentes = await conn.fetchval(
                "SELECT COUNT(*) FROM pedidos_setores WHERE pedido_id=$1 AND status='pendente'",
                setor_rec["pedido_id"],
            )
            if pendentes == 0:
                await conn.execute(
                    "UPDATE pedidos SET status='pronto', pronto_at=NOW() WHERE id=$1",
                    setor_rec["pedido_id"],
                )

        # Supabase Realtime detecta as alterações no banco automaticamente
        return await get_pedido(conn, setor_rec["pedido_id"])
