import re
from typing import List, Dict
import asyncpg


async def _gerar_codigo(conn: asyncpg.Connection) -> str:
    row = await conn.fetchrow("SELECT codigo FROM pedidos ORDER BY id DESC LIMIT 1")
    if not row:
        return "PE001"
    m = re.search(r"\d+", row["codigo"])
    n = int(m.group()) + 1 if m else 1
    return f"PE{n:03d}"


async def criar_pedido(
    conn: asyncpg.Connection,
    mesa_id: int,
    itens: List[Dict],
    observacao: str = None,
) -> Dict:
    async with conn.transaction():
        mesa = await conn.fetchrow("SELECT * FROM mesas WHERE id = $1", mesa_id)
        if not mesa:
            raise ValueError("Mesa não encontrada")

        ids = [i["produto_id"] for i in itens]
        produtos = await conn.fetch(
            "SELECT * FROM produtos WHERE id = ANY($1::int[]) AND ativo = TRUE", ids
        )
        pmap = {p["id"]: dict(p) for p in produtos}

        for item in itens:
            if item["produto_id"] not in pmap:
                raise ValueError(f"Produto ID {item['produto_id']} não encontrado ou inativo")

        valor_total = sum(
            pmap[i["produto_id"]]["preco"] * i["quantidade"] for i in itens
        )

        # Tempo estimado: paralelo por setor (pega o maior)
        setor_tempos: Dict[str, int] = {}
        for item in itens:
            p = pmap[item["produto_id"]]
            s = p["setor"]
            t = p["tempo_preparo"] * item["quantidade"]
            setor_tempos[s] = max(setor_tempos.get(s, 0), t)

        tempo_estimado = max(setor_tempos.values()) if setor_tempos else 15
        codigo = await _gerar_codigo(conn)

        pedido = await conn.fetchrow(
            """INSERT INTO pedidos (codigo, mesa_id, valor_total, tempo_estimado, observacao)
               VALUES ($1,$2,$3,$4,$5) RETURNING *""",
            codigo, mesa_id, valor_total, tempo_estimado, observacao,
        )
        pid = pedido["id"]

        for item in itens:
            p = pmap[item["produto_id"]]
            await conn.execute(
                """INSERT INTO itens_pedido
                   (pedido_id, produto_id, quantidade, preco_unitario, subtotal)
                   VALUES ($1,$2,$3,$4,$5)""",
                pid, item["produto_id"], item["quantidade"],
                p["preco"], p["preco"] * item["quantidade"],
            )

        for setor in setor_tempos:
            await conn.execute(
                "INSERT INTO pedidos_setores (pedido_id, setor) VALUES ($1,$2)",
                pid, setor,
            )

        await conn.execute("UPDATE mesas SET status='ocupada' WHERE id=$1", mesa_id)
        return await get_pedido(conn, pid)


async def get_pedido(conn: asyncpg.Connection, pedido_id: int) -> Dict:
    p = await conn.fetchrow(
        """SELECT p.*, m.numero AS mesa_numero
           FROM pedidos p JOIN mesas m ON m.id = p.mesa_id
           WHERE p.id = $1""",
        pedido_id,
    )
    if not p:
        return None

    itens = await conn.fetch(
        """SELECT ip.*, pr.nome AS produto_nome, pr.setor, pr.categoria
           FROM itens_pedido ip JOIN produtos pr ON pr.id = ip.produto_id
           WHERE ip.pedido_id = $1 ORDER BY ip.id""",
        pedido_id,
    )
    setores = await conn.fetch(
        "SELECT * FROM pedidos_setores WHERE pedido_id=$1 ORDER BY setor", pedido_id
    )

    return {
        "id":             p["id"],
        "codigo":         p["codigo"],
        "mesa":           {"id": p["mesa_id"], "numero": p["mesa_numero"]},
        "status":         p["status"],
        "valor_total":    float(p["valor_total"]),
        "tempo_estimado": p["tempo_estimado"],
        "observacao":     p["observacao"],
        "created_at":     p["created_at"].isoformat() if p["created_at"] else None,
        "pronto_at":      p["pronto_at"].isoformat()   if p["pronto_at"]   else None,
        "entrega_at":     p["entrega_at"].isoformat()  if p["entrega_at"]  else None,
        "finalizado_at":  p["finalizado_at"].isoformat() if p["finalizado_at"] else None,
        "itens": [
            {
                "id":             i["id"],
                "produto_id":     i["produto_id"],
                "produto_nome":   i["produto_nome"],
                "setor":          i["setor"],
                "categoria":      i["categoria"],
                "quantidade":     i["quantidade"],
                "preco_unitario": float(i["preco_unitario"]),
                "subtotal":       float(i["subtotal"]),
            }
            for i in itens
        ],
        "setores": [
            {
                "id":           s["id"],
                "setor":        s["setor"],
                "status":       s["status"],
                "concluido_at": s["concluido_at"].isoformat() if s["concluido_at"] else None,
            }
            for s in setores
        ],
    }
