"""
tabuleiros.py
Funções para criar e desenhar tabuleiros (matrizes) do jogo.

Inclui função para desenhar tabuleiro combinado (naves + tiros),
com suporte a X colorido de acordo com a cor da nave atingida.
"""

from typing import List, Tuple, Dict, Optional
from naves import ANSI_CORES, ANSI_RESET

def criar_tabuleiro(size: int) -> List[List[str]]:
    """Cria uma matriz size x size preenchida com '.' (vazio)."""
    return [["." for _ in range(size)] for _ in range(size)]

def desenhar_tabuleiro_combinado(size: int,
                                 pos_naves_info: Dict[Tuple[int,int], Tuple[str, Optional[str]]],
                                 tiros: List[Tuple[int,int]],
                                 tiros_acerto_colors_map: Dict[Tuple[int,int], str]) -> str:
    """
    Retorna string com representação do tabuleiro combinado:
    - pos_naves_info: {(r,c): (simbolo, cor_str)} para Naves vivas (apresentadas com a cor da nave)
    - tiros: lista de (r,c) com todos os tiros efetuados (acertos e misses)
    - tiros_acerto_colors_map: {(r,c): cor_str} para posições que acertaram, mapping para a cor da nave atingida
    Regras de desenho por célula:
    - Se a célula foi alvo de um tiro acertado (presente em tiros_acerto_colors_map): mostrar 'X' com cor da nave.
    - Else se a célula contém uma nave viva: mostrar o símbolo da nave com a cor da nave.
    - Else se a célula foi alvo de um tiro (miss): mostrar 'o' (miss) sem cor.
    - Else: '.' vazio
    """
    tiros_set = set(tiros)
    linhas = []
    header = "   " + " ".join(f"{i:2}" for i in range(size))
    linhas.append(header)
    for r in range(size):
        linha = f"{r:2} "
        for c in range(size):
            pos = (r,c)
            ch = "."
            codigo = ""
            # prioridade: tiro acerto
            if pos in tiros_acerto_colors_map:
                cor = tiros_acerto_colors_map[pos] or ""
                codigo = ANSI_CORES.get(cor.lower(), "")
                ch = "X"
            elif pos in pos_naves_info:
                simbolo, cor = pos_naves_info[pos]
                codigo = ANSI_CORES.get((cor or "").lower(), "")
                ch = simbolo
            elif pos in tiros_set:
                ch = "o"
                codigo = ""  # miss no color
            # garantir reset
            if codigo:
                linha += f" {codigo}{ch}{ANSI_RESET}"
            else:
                linha += f" {ch}"
        linhas.append(linha)
    return "\n".join(linhas)

def validar_posicao(pos: Tuple[int,int], size: int) -> bool:
    r, c = pos
    return 0 <= r < size and 0 <= c < size