-- ============================================================
-- Cachoeira Bar e Petiscaria — Schema PostgreSQL (Supabase)
-- ============================================================

CREATE TABLE IF NOT EXISTS usuarios (
    id          SERIAL PRIMARY KEY,
    nome        VARCHAR(200) NOT NULL,
    email       VARCHAR(200) UNIQUE NOT NULL,
    senha_hash  VARCHAR(500) NOT NULL,
    perfil      VARCHAR(50) NOT NULL CHECK (perfil IN ('administrador','recepcionista','cozinheiro','churrasqueiro','garcom')),
    ativo       BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS mesas (
    id         SERIAL PRIMARY KEY,
    numero     VARCHAR(10) UNIQUE NOT NULL,
    status     VARCHAR(20) DEFAULT 'livre' CHECK (status IN ('livre','ocupada')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS produtos (
    id            SERIAL PRIMARY KEY,
    nome          VARCHAR(200) NOT NULL,
    categoria     VARCHAR(50) NOT NULL CHECK (categoria IN ('almoco','petisco','bebida')),
    preco         DECIMAL(10,2) NOT NULL,
    unidade       VARCHAR(50) DEFAULT 'unidade',
    tempo_preparo INTEGER DEFAULT 15,
    setor         VARCHAR(50) NOT NULL CHECK (setor IN ('balcao_01','balcao_02','balcao_03','churrasqueira')),
    ativo         BOOLEAN DEFAULT TRUE,
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS pedidos (
    id             SERIAL PRIMARY KEY,
    codigo         VARCHAR(20) UNIQUE NOT NULL,
    mesa_id        INTEGER REFERENCES mesas(id),
    status         VARCHAR(30) DEFAULT 'em_producao'
                   CHECK (status IN ('em_producao','pronto','em_entrega','finalizado')),
    valor_total    DECIMAL(10,2) DEFAULT 0,
    tempo_estimado INTEGER DEFAULT 0,
    observacao     TEXT,
    created_at     TIMESTAMPTZ DEFAULT NOW(),
    pronto_at      TIMESTAMPTZ,
    entrega_at     TIMESTAMPTZ,
    finalizado_at  TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS itens_pedido (
    id             SERIAL PRIMARY KEY,
    pedido_id      INTEGER REFERENCES pedidos(id) ON DELETE CASCADE,
    produto_id     INTEGER REFERENCES produtos(id),
    quantidade     INTEGER NOT NULL CHECK (quantidade > 0),
    preco_unitario DECIMAL(10,2) NOT NULL,
    subtotal       DECIMAL(10,2) NOT NULL,
    created_at     TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS pedidos_setores (
    id           SERIAL PRIMARY KEY,
    pedido_id    INTEGER REFERENCES pedidos(id) ON DELETE CASCADE,
    setor        VARCHAR(50) NOT NULL,
    status       VARCHAR(30) DEFAULT 'pendente' CHECK (status IN ('pendente','concluido')),
    concluido_at TIMESTAMPTZ,
    created_at   TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (pedido_id, setor)
);

-- ── Supabase Realtime ──────────────────────────────────────────────────────
-- Habilita notificações em tempo real para o frontend via Supabase Realtime
ALTER PUBLICATION supabase_realtime ADD TABLE pedidos;
ALTER PUBLICATION supabase_realtime ADD TABLE pedidos_setores;
ALTER PUBLICATION supabase_realtime ADD TABLE mesas;

-- Índices
CREATE INDEX IF NOT EXISTS idx_pedidos_status     ON pedidos(status);
CREATE INDEX IF NOT EXISTS idx_pedidos_mesa_id    ON pedidos(mesa_id);
CREATE INDEX IF NOT EXISTS idx_pedidos_created_at ON pedidos(created_at);
CREATE INDEX IF NOT EXISTS idx_itens_pedido_id    ON itens_pedido(pedido_id);
CREATE INDEX IF NOT EXISTS idx_setores_pedido     ON pedidos_setores(pedido_id);
CREATE INDEX IF NOT EXISTS idx_setores_setor      ON pedidos_setores(setor, status);
CREATE INDEX IF NOT EXISTS idx_usuarios_email     ON usuarios(email);
