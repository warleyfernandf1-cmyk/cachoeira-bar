from pydantic import BaseModel, field_validator
from typing import List, Optional
from enum import Enum


class Perfil(str, Enum):
    administrador  = "administrador"
    recepcionista  = "recepcionista"
    cozinheiro     = "cozinheiro"
    churrasqueiro  = "churrasqueiro"
    garcom         = "garcom"


class Categoria(str, Enum):
    almoco  = "almoco"
    petisco = "petisco"
    bebida  = "bebida"


class Setor(str, Enum):
    balcao_01     = "balcao_01"
    balcao_02     = "balcao_02"
    balcao_03     = "balcao_03"
    churrasqueira = "churrasqueira"


# ── Auth ──────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: str
    senha: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    perfil: str
    nome: str


# ── Usuários ──────────────────────────────────────────────────────────────────

class UsuarioCreate(BaseModel):
    nome: str
    email: str
    senha: str
    perfil: Perfil


class UsuarioUpdate(BaseModel):
    nome:   Optional[str]   = None
    email:  Optional[str]   = None
    senha:  Optional[str]   = None
    perfil: Optional[Perfil] = None
    ativo:  Optional[bool]  = None


# ── Produtos ──────────────────────────────────────────────────────────────────

class ProdutoCreate(BaseModel):
    nome:          str
    categoria:     Categoria
    preco:         float
    unidade:       str = "unidade"
    tempo_preparo: int = 15
    setor:         Setor


class ProdutoUpdate(BaseModel):
    nome:          Optional[str]       = None
    categoria:     Optional[Categoria] = None
    preco:         Optional[float]     = None
    unidade:       Optional[str]       = None
    tempo_preparo: Optional[int]       = None
    setor:         Optional[Setor]     = None
    ativo:         Optional[bool]      = None


# ── Pedidos ───────────────────────────────────────────────────────────────────

class ItemPedidoCreate(BaseModel):
    produto_id: int
    quantidade: int

    @field_validator("quantidade")
    @classmethod
    def validar_quantidade(cls, v):
        if v <= 0:
            raise ValueError("Quantidade deve ser maior que zero")
        return v


class PedidoCreate(BaseModel):
    mesa_id:    int
    itens:      List[ItemPedidoCreate]
    observacao: Optional[str] = None

    @field_validator("itens")
    @classmethod
    def validar_itens(cls, v):
        if not v:
            raise ValueError("O pedido deve ter pelo menos um item")
        return v


# ── Mesas ─────────────────────────────────────────────────────────────────────

class MesaCreate(BaseModel):
    numero: str
