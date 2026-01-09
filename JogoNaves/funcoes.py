"""
funcoes.py
Funções utilitárias: menu, capa, guardar/carregar jogo, geração de posições únicas, leitura de tiros.
"""

import os
import json
import random
from typing import Tuple, List, Dict

from naves import NaveModelo, NaveComExtra, ANSI_CORES, ANSI_RESET
from tabuleiros import validar_posicao

SAVE_FILENAME = "save_nave_jogo.json"

def limpar_ecra():
    os.system("cls" if os.name == "nt" else "clear")

def capa():
    limpar_ecra()
    art_lines = [
        "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",
        "~~~~~~~~~~~~ JOGO DA NAVE ~~~~~~~~~~~",
        "~~~~~~~~~ de SAMUEL TORRES ~~~~~~~~~~",
        "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",
        "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",
        "~~~~~~/     (     ()     )    \\~~~~~~",
        "~~~~~~| |    \\-- /||\\ --/    | |~~~~~",
        "=~~~~~=\\ \\^   \\  (--)  /   ^/ /=~~~==",
        "=~~~====\\ \\^   |------|   ^/ /====~~=",
        "====~~===\\ \\   |_/  \\_|   / /==~~====",
        "=~~===~~==\\O   |/    \\|   O/======~~=",
        "====~~=====\\   ||    ||   /~~===~~===",
        "==~~========\\  `´    `´  /===========",
        "=============\\          /====~~======",
        "==============\\        /=============",
        "===============\\      /==============",
        "================\\    /===============",
        "=================\\  /================",
        "==================\\/=================",
        "====================================="
    ]

    # cores desejadas: '~' => magenta (roxo), '=' => azul
    magenta_code = ANSI_CORES.get("magenta", "")
    azul_code = ANSI_CORES.get("azul", "")
    reset = ANSI_RESET

    def colorize_line(line: str) -> str:
        # agrupa sequências de '~' e '=' para evitar muitos resets
        res_parts = []
        i = 0
        n = len(line)
        while i < n:
            ch = line[i]
            if ch == "~":
                j = i
                while j < n and line[j] == "~":
                    j += 1
                chunk = line[i:j]
                if magenta_code:
                    res_parts.append(f"{magenta_code}{chunk}{reset}")
                else:
                    res_parts.append(chunk)
                i = j
            elif ch == "=":
                j = i
                while j < n and line[j] == "=":
                    j += 1
                chunk = line[i:j]
                if azul_code:
                    res_parts.append(f"{azul_code}{chunk}{reset}")
                else:
                    res_parts.append(chunk)
                i = j
            else:
                # caracteres normais copiados até encontrar ~ ou =
                j = i
                while j < n and line[j] not in ("~", "="):
                    j += 1
                res_parts.append(line[i:j])
                i = j
        return "".join(res_parts)

    for line in art_lines:
        print(colorize_line(line))

def menu() -> str:
    print("Menu:")
    print("1 - Novo Jogo")
    print("2 - Carregar Jogo")
    print("3 - Guardar Jogo")
    print("4 - Sair")
    escolha = input("Escolha uma opção (1-4): ").strip()
    return escolha

def gerar_posicao_aleatoria(size: int, ocupadas: set) -> Tuple[int,int]:
    """Gera posição aleatória não presente em ocupadas."""
    while True:
        r = random.randrange(size)
        c = random.randrange(size)
        if (r,c) not in ocupadas:
            return (r,c)

def gerar_n_posicoes_unicas(size: int, n: int) -> List[Tuple[int,int]]:
    ocupadas = set()
    posicoes = []
    while len(posicoes) < n:
        p = gerar_posicao_aleatoria(size, ocupadas)
        posicoes.append(p)
        ocupadas.add(p)
    return posicoes

def ler_tiro_manual(size: int, tiros_existentes: set) -> Tuple[int,int]:
    """
    Lê uma coordenada do utilizador no formato linha,coluna (ex: 2,3).
    Aceita 'r' para gerar um tiro aleatório único (respeitando tiros_existentes).
    Garante que a posição está dentro do tabuleiro e não repetida.
    """
    while True:
        entrada = input("Introduza tiro (linha,coluna) ex: 2,3  ou 'r' para aleatório: ").strip()
        if entrada.lower() == "r":
            # gerar aleatório não repetido
            while True:
                r = random.randrange(size)
                c = random.randrange(size)
                if (r,c) not in tiros_existentes:
                    return (r,c)
        # tentar parse "linha,coluna"
        if "," in entrada:
            try:
                parts = entrada.split(",")
                r = int(parts[0].strip())
                c = int(parts[1].strip())
                if not validar_posicao((r,c), size):
                    print("Posição fora do tabuleiro. Tente novamente.")
                    continue
                if (r,c) in tiros_existentes:
                    print("Já foi efetuado um tiro nessa posição. Tente outra.")
                    continue
                return (r,c)
            except Exception:
                print("Formato inválido. Tente novamente.")
        else:
            print("Formato inválido. Use linha,coluna (ex: 2,3) ou 'r'.")

def save_game(state: dict, filename: str = SAVE_FILENAME) -> bool:
    """
    Guarda o dicionário state em JSON no filename.
    state deverá conter apenas estruturas serializáveis (listas e dicionários com tipos simples).
    Nota: quem chama esta função deve converter tuplos para listas e similarmente os mapas
    de cores para formas serializáveis.
    """
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print("Erro ao guardar:", e)
        return False

def load_game(filename: str = SAVE_FILENAME) -> dict:
    """Carrega ficheiro JSON e devolve dicionário (lança exceção se não existir)."""
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

def serializar_nave_obj(nave):
    """Converte objeto de nave para dict serializável, incluindo posição se houver."""
    d = nave.to_dict()
    return d

def desserializar_nave_dict(d: dict):
    """Cria objeto NaveModelo ou NaveComExtra a partir do dict."""
    cls = d.get("class", "NaveModelo")
    if cls == "NaveComExtra":
        return NaveComExtra.from_dict(d)
    else:
        return NaveModelo.from_dict(d)