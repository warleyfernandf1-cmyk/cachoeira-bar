# Cachoeira Bar e Petiscaria — Sistema Operacional

Sistema web completo para controle de restaurante/petiscaria.

---

## Stack (apenas 2 plataformas)

| Camada   | Tecnologia |
|----------|-----------|
| API REST | FastAPI + mangum → **Vercel** (serverless Python) |
| Banco    | PostgreSQL → **Supabase** |
| Realtime | Supabase Realtime (postgres_changes) |
| Frontend | HTML + CSS + JS → **Vercel** (estático) |

---

## Perfis de Acesso (RBAC)

| Perfil         | Páginas permitidas |
|----------------|-------------------|
| Administrador  | Todas |
| Recepcionista  | Recepção |
| Cozinheiro     | Produção (Balcões 01, 02, 03) |
| Churrasqueiro  | Produção (Churrasqueira) |
| Garçom         | Expedição |

---

## Execução Local

### 1. Banco de dados (Supabase)

1. Crie um projeto em [supabase.com](https://supabase.com)
2. SQL Editor → execute `sql/schema.sql`
3. SQL Editor → execute `sql/seed.sql`
4. Copie as credenciais em **Project Settings > API**:
   - `URL` → `SUPABASE_URL` no config.js
   - `anon public` key → `SUPABASE_KEY` no config.js
5. Copie a **Connection String do Pooler** (Transaction mode, porta 6543):
   - Project Settings > Database > Connection pooling > URI
   - Use esta URL como `DATABASE_URL` no `.env`

### 2. Backend (local)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt

cp .env.example .env
# Edite .env com DATABASE_URL e SECRET_KEY
```

```bash
# Rodar o servidor
uvicorn main:app --reload --port 8000
```

### 3. Criar Admin (primeira vez)

```bash
curl -X POST http://localhost:8000/api/auth/setup-admin
```

Credenciais criadas: `admin@cachoeira.com` / `Admin@123`

> Troque a senha em Cadastro → Usuários após o primeiro login.

### 4. Frontend (local)

Edite `frontend/static/config.js`:
```js
const CONFIG = {
  API:           "http://localhost:8000",  // backend local
  SUPABASE_URL:  "https://xxx.supabase.co",
  SUPABASE_KEY:  "eyJ...",
};
```

Abra `frontend/` com Live Server (VS Code) ou:
```bash
cd frontend
python -m http.server 5500
```

Acesse: [http://localhost:5500](http://localhost:5500)

---

## Deploy em Produção (Vercel + Supabase)

### Passo 1 — Vercel

1. Crie conta em [vercel.com](https://vercel.com)
2. New Project → Import Git Repository → selecione este repositório
3. Framework: **Other** | Root Directory: `/` (raiz)
4. Adicione as variáveis de ambiente:

| Variável       | Valor |
|----------------|-------|
| `DATABASE_URL` | Connection string do Supabase Pooler (porta 6543) |
| `SECRET_KEY`   | Chave aleatória (`python -c "import secrets; print(secrets.token_hex(32))"`) |
| `FRONTEND_URL` | URL do Vercel (ex: `https://cachoeira.vercel.app`) |

5. Deploy

### Passo 2 — Atualizar config.js

Após o deploy, edite `frontend/static/config.js`:

```js
const CONFIG = {
  API:           "",                          // vazio = mesma origin (Vercel)
  SUPABASE_URL:  "https://xxx.supabase.co",
  SUPABASE_KEY:  "eyJ...",
};
```

Commit + push → Vercel faz redeploy automático.

### Passo 3 — Criar admin em produção

```bash
curl -X POST https://SEU-PROJETO.vercel.app/api/auth/setup-admin
```

---

## Estrutura do Projeto

```
cachoeira-bar/
├── api/
│   └── index.py            ← Entry point Vercel (mangum wraps FastAPI)
├── requirements.txt        ← Deps para Vercel instalar
├── sql/
│   ├── schema.sql          ← Tabelas + Supabase Realtime publication
│   └── seed.sql            ← 30 mesas + produtos de exemplo
├── backend/
│   ├── main.py             ← App FastAPI
│   ├── dependencies.py     ← JWT auth + RBAC
│   ├── models/
│   │   ├── database.py     ← acquire() — conexão por request (serverless-safe)
│   │   └── schemas.py      ← Pydantic schemas
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── pedido_service.py
│   │   └── impressao_service.py
│   └── routes/
│       ├── auth.py
│       ├── usuarios.py
│       ├── produtos.py
│       ├── mesas.py
│       ├── pedidos.py
│       ├── producao.py
│       ├── expedicao.py
│       └── dashboard.py
├── frontend/
│   ├── index.html          ← Login
│   ├── recepcao/
│   ├── producao/
│   ├── expedicao/
│   ├── dashboard/
│   ├── cadastro/
│   └── static/
│       ├── config.js       ← ⚠ Alterar antes do deploy
│       ├── auth.js         ← JWT helpers + Supabase Realtime
│       └── style.css
└── vercel.json             ← Roteia /api/* → Python, resto → frontend/
```

---

## Como funciona o Realtime

Sem WebSocket próprio. O Supabase monitora as tabelas `pedidos`, `pedidos_setores` e `mesas` via PostgreSQL replication. Quando o backend escreve no banco, o Supabase notifica automaticamente todos os frontends conectados.

```
Backend escreve no banco (INSERT/UPDATE)
    ↓
Supabase detecta via postgres_changes
    ↓
Supabase Realtime envia evento para todos os clientes JS conectados
    ↓
Frontend recarrega os dados relevantes (sem reload de página)
```

---

## Fluxo Completo

```
Login → Recepção (mesa → pedido → confirma)
     → [Supabase Realtime] → Produção (setores veem seus itens)
     → Setor conclui → [todos prontos?] → Pedido = PRONTO
     → [Supabase Realtime] → Expedição (garçom entrega → finaliza)
     → Mesa liberada automaticamente
```

---

## Impressão por Setor

Atualmente simulada no console do servidor. Para impressora térmica real:

1. Instale `python-escpos` no backend
2. Em `services/impressao_service.py`, substitua `print(ficha)` pela chamada ESC/POS
3. Mapeie setor → IP da impressora na rede local
