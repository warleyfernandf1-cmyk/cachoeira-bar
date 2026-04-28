import asyncpg
import os
from contextlib import asynccontextmanager


def _url() -> str:
    raw = os.getenv("DATABASE_URL", "")
    if not raw:
        raise RuntimeError("DATABASE_URL não definida no .env")
    # asyncpg exige postgresql://, não postgres://
    return raw.replace("postgres://", "postgresql://", 1)


@asynccontextmanager
async def acquire():
    """
    Abre uma conexão por request e a fecha ao sair.
    Compatível com serverless (Vercel) — usa o PgBouncer do Supabase (porta 6543).
    """
    conn = await asyncpg.connect(_url())
    try:
        yield conn
    finally:
        await conn.close()
