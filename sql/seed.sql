-- ============================================================
-- Seed — 30 mesas + produtos de exemplo
-- Admin criado via: POST /api/auth/setup-admin (primeira vez)
-- ============================================================

-- Mesas M01..M30
INSERT INTO mesas (numero) VALUES
  ('M01'),('M02'),('M03'),('M04'),('M05'),('M06'),('M07'),('M08'),('M09'),('M10'),
  ('M11'),('M12'),('M13'),('M14'),('M15'),('M16'),('M17'),('M18'),('M19'),('M20'),
  ('M21'),('M22'),('M23'),('M24'),('M25'),('M26'),('M27'),('M28'),('M29'),('M30')
ON CONFLICT (numero) DO NOTHING;

-- Produtos — Almoço (Balcão 01)
INSERT INTO produtos (nome, categoria, preco, unidade, tempo_preparo, setor) VALUES
  ('Prato Executivo',         'almoco', 25.00, 'prato',   20, 'balcao_01'),
  ('Marmitex Pequena',        'almoco', 16.00, 'unidade', 15, 'balcao_01'),
  ('Marmitex Grande',         'almoco', 22.00, 'unidade', 15, 'balcao_01'),
  ('Prato Feito',             'almoco', 20.00, 'prato',   18, 'balcao_01')
ON CONFLICT DO NOTHING;

-- Produtos — Petisco (Balcão 02)
INSERT INTO produtos (nome, categoria, preco, unidade, tempo_preparo, setor) VALUES
  ('Batata Frita (P)',        'petisco', 18.00, 'porção', 15, 'balcao_02'),
  ('Batata Frita (G)',        'petisco', 28.00, 'porção', 18, 'balcao_02'),
  ('Mandioca Frita',          'petisco', 20.00, 'porção', 18, 'balcao_02'),
  ('Calabresa Acebolada',     'petisco', 28.00, 'porção', 20, 'balcao_02'),
  ('Camarão na Moranga',      'petisco', 55.00, 'porção', 25, 'balcao_02'),
  ('Bolinho de Bacalhau',     'petisco', 32.00, 'porção', 20, 'balcao_02')
ON CONFLICT DO NOTHING;

-- Produtos — Churrasco (Churrasqueira)
INSERT INTO produtos (nome, categoria, preco, unidade, tempo_preparo, setor) VALUES
  ('Linguiça Toscana',        'petisco', 26.00, 'porção', 25, 'churrasqueira'),
  ('Queijo Coalho Grelhado',  'petisco', 22.00, 'porção', 15, 'churrasqueira'),
  ('Frango na Brasa (P)',     'petisco', 35.00, 'porção', 30, 'churrasqueira'),
  ('Frango na Brasa (G)',     'petisco', 55.00, 'porção', 35, 'churrasqueira'),
  ('Costela Bovina',          'petisco', 65.00, 'kg',     45, 'churrasqueira'),
  ('Picanha Grelhada',        'petisco', 75.00, 'porção', 35, 'churrasqueira')
ON CONFLICT DO NOTHING;

-- Produtos — Bebidas (Balcão 03)
INSERT INTO produtos (nome, categoria, preco, unidade, tempo_preparo, setor) VALUES
  ('Água Mineral',            'bebida',  4.00, 'garrafa',  2, 'balcao_03'),
  ('Refrigerante Lata',       'bebida',  6.00, 'lata',     2, 'balcao_03'),
  ('Suco Natural',            'bebida', 10.00, 'copo',     5, 'balcao_03'),
  ('Cerveja Long Neck',       'bebida',  9.00, 'unidade',  2, 'balcao_03'),
  ('Cerveja Lata 350ml',      'bebida',  7.00, 'lata',     2, 'balcao_03'),
  ('Caipirinha',              'bebida', 18.00, 'copo',     5, 'balcao_03'),
  ('Caipiroska',              'bebida', 20.00, 'copo',     5, 'balcao_03'),
  ('Dose de Cachaça',         'bebida', 12.00, 'dose',     2, 'balcao_03')
ON CONFLICT DO NOTHING;
