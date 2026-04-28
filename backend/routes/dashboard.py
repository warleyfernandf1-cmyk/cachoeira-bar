from fastapi import APIRouter, Depends
from models.database import acquire
from dependencies import get_current_user
from datetime import datetime, timezone

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("")
async def stats(_: dict = Depends(get_current_user)):
    async with acquire() as conn:
        total_hoje  = await conn.fetchval(
            "SELECT COUNT(*) FROM pedidos WHERE DATE(created_at AT TIME ZONE 'America/Sao_Paulo') = CURRENT_DATE"
        )
        em_producao = await conn.fetchval("SELECT COUNT(*) FROM pedidos WHERE status='em_producao'")
        prontos     = await conn.fetchval("SELECT COUNT(*) FROM pedidos WHERE status='pronto'")
        em_entrega  = await conn.fetchval("SELECT COUNT(*) FROM pedidos WHERE status='em_entrega'")
        finalizados = await conn.fetchval(
            "SELECT COUNT(*) FROM pedidos WHERE status='finalizado' AND DATE(created_at AT TIME ZONE 'America/Sao_Paulo') = CURRENT_DATE"
        )
        avg_raw = await conn.fetchval(
            """SELECT AVG(EXTRACT(EPOCH FROM (pronto_at - created_at)) / 60)
               FROM pedidos
               WHERE pronto_at IS NOT NULL
                 AND DATE(created_at AT TIME ZONE 'America/Sao_Paulo') = CURRENT_DATE"""
        )
        setor_rows = await conn.fetch(
            """SELECT setor, AVG(EXTRACT(EPOCH FROM (concluido_at - created_at)) / 60) AS avg_min
               FROM pedidos_setores
               WHERE concluido_at IS NOT NULL
                 AND DATE(created_at AT TIME ZONE 'America/Sao_Paulo') = CURRENT_DATE
               GROUP BY setor"""
        )
        ativos = await conn.fetch(
            """SELECT p.codigo, m.numero AS mesa, p.status, p.tempo_estimado, p.created_at
               FROM pedidos p JOIN mesas m ON m.id = p.mesa_id
               WHERE p.status IN ('em_producao','pronto','em_entrega')
               ORDER BY p.created_at ASC"""
        )

    now = datetime.now(timezone.utc)
    pedidos_ativos = []
    for r in ativos:
        elapsed  = (now - r["created_at"]).total_seconds() / 60
        tempo    = r["tempo_estimado"] or 15
        atrasado = r["status"] == "em_producao" and elapsed > tempo * 1.2
        pedidos_ativos.append({
            "codigo":         r["codigo"],
            "mesa":           r["mesa"],
            "status":         "atrasado" if atrasado else r["status"],
            "tempo_estimado": tempo,
            "elapsed_min":    round(elapsed, 1),
            "created_at":     r["created_at"].isoformat(),
        })

    return {
        "stats": {
            "total_hoje":          int(total_hoje),
            "em_producao":         int(em_producao),
            "prontos":             int(prontos),
            "em_entrega":          int(em_entrega),
            "finalizados":         int(finalizados),
            "tempo_medio_minutos": round(float(avg_raw), 1) if avg_raw else 0,
        },
        "por_setor":      {r["setor"]: round(float(r["avg_min"]), 1) for r in setor_rows},
        "pedidos_ativos": pedidos_ativos,
    }
