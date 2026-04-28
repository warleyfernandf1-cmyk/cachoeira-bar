import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import auth, usuarios, produtos, mesas, pedidos, producao, expedicao, dashboard

load_dotenv()

app = FastAPI(title="Cachoeira Bar e Petiscaria", version="1.0.0")

frontend_url = os.getenv("FRONTEND_URL", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url] if frontend_url != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,      prefix="/api")
app.include_router(usuarios.router,  prefix="/api")
app.include_router(produtos.router,  prefix="/api")
app.include_router(mesas.router,     prefix="/api")
app.include_router(pedidos.router,   prefix="/api")
app.include_router(producao.router,  prefix="/api")
app.include_router(expedicao.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")


@app.get("/")
async def root():
    return {"status": "ok", "sistema": "Cachoeira Bar e Petiscaria"}
