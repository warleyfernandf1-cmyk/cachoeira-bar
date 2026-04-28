from datetime import datetime
from typing import Dict, List

NOMES_SETORES = {
    "balcao_01":    "BALCÃO 01",
    "balcao_02":    "BALCÃO 02",
    "balcao_03":    "BALCÃO 03",
    "churrasqueira": "CHURRASQUEIRA",
}


def _formatar_ficha(codigo: str, mesa: str, setor: str, itens: List[Dict], horario: datetime) -> str:
    nome = NOMES_SETORES.get(setor, setor.upper())
    linhas = [
        "=" * 42,
        "     CACHOEIRA BAR E PETISCARIA",
        "=" * 42,
        f"  PEDIDO : {codigo}",
        f"  MESA   : {mesa}",
        f"  SETOR  : {nome}",
        f"  HORA   : {horario.strftime('%d/%m/%Y %H:%M')}",
        "-" * 42,
        "  ITENS:",
    ]
    for item in itens:
        linha = f"  {item['quantidade']:>2}x  {item['produto_nome']}"
        linhas.append(linha)
    linhas.append("=" * 42)
    return "\n".join(linhas)


def imprimir_pedido(pedido: Dict) -> Dict[str, str]:
    """
    Separa itens por setor, formata e imprime fichas.
    Retorna dict {setor: texto_ficha} para futura integração com impressora térmica.
    """
    codigo  = pedido["codigo"]
    mesa    = pedido["mesa"]["numero"]
    raw_ts  = pedido.get("created_at")
    horario = datetime.fromisoformat(raw_ts) if raw_ts else datetime.now()

    # Agrupar itens por setor
    por_setor: Dict[str, List] = {}
    for item in pedido["itens"]:
        por_setor.setdefault(item["setor"], []).append(item)

    fichas: Dict[str, str] = {}
    for setor, itens in por_setor.items():
        ficha = _formatar_ficha(codigo, mesa, setor, itens, horario)
        fichas[setor] = ficha
        print(f"\n{ficha}")  # Simulação de impressão no console

    return fichas
