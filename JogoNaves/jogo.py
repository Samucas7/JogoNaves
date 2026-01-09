"""
jogo.py
Ficheiro principal: orquestra o jogo usando naves.py, tabuleiros.py e funcoes.py

Alterações implementadas:
- BOARD_SIZE = 6
- Tabuleiro combinado (naves + tiros) apresenta apenas os tiros da ronda atual (3 tiros)
- 'X' dos acertos aparece com a cor da nave atingida (apenas para acertos da ronda atual)
- Após mostrar o resultado da ronda, as naves são reposicionadas apenas quando o jogador continua
- Guarda/Carrega mantidos
"""

import random
import time
from typing import Tuple, List, Dict, Set

from naves import NaveModelo, NaveComExtra
from tabuleiros import desenhar_tabuleiro_combinado
import funcoes as F

BOARD_SIZE = 6  # dimensão do tabuleiro agora 6x6
MAX_TIRO = 105
ENERGIA_BONUS_TIRO = 45  # ao atingir este total de tiros, aplica energia_extra às naves

SAVE_FILENAME = "save_nave_jogo.json"

def criar_naves_padroes() -> List[Tuple[object, Tuple[int,int]]]:
    esqueleto = NaveModelo(nome="esqueleto", cor="verde", energia=100, perderEnergia=50, simbolo="E")
    normal = NaveModelo(nome="normal", cor="amarelo", energia=100, perderEnergia=35, simbolo="N")
    lutador = NaveComExtra(nome="lutador", cor="ciano", energia=100, perderEnergia=30, simbolo="L", energia_extra=10)
    bombardeiro = NaveComExtra(nome="bombardeiro", cor="azul", energia=100, perderEnergia=30, simbolo="B", energia_extra=30)
    gigante = NaveComExtra(nome="gigante", cor="magenta", energia=100, perderEnergia=25, simbolo="G", energia_extra=40)
    titan = NaveComExtra(nome="titan", cor="vermelho", energia=100, perderEnergia=20, simbolo="T", energia_extra=50)
    return [(esqueleto, None), (normal, None), (lutador, None), (bombardeiro, None), (gigante, None), (titan, None)]

def mostrar_menu_selecao_naves(naves_all: List[Tuple[object, Tuple[int,int]]], selecionados: Set[int] = None):
    from naves import ANSI_CORES, ANSI_RESET
    if selecionados is None:
        selecionados = set()
    print("Naves disponíveis:")
    for idx, (nave, _) in enumerate(naves_all, start=1):
        energia_extra = getattr(nave, "energia_extra", None)
        linha = f"{idx} - {nave.nome} | Energia: {nave.energia} | Perda: {nave.perderEnergia} | Símbolo: {nave.simbolo}"
        if energia_extra is not None:
            linha += f" | Energia extra: {energia_extra}"
        linha += f" | Cor: {nave.cor}"
        if idx in selecionados:
            codigo = ANSI_CORES.get("preto", "")
        else:
            codigo = ANSI_CORES.get((nave.cor or "").lower(), "")
        print(f"{codigo}{linha}{ANSI_RESET}")

def escolher_3_naves(naves_all: List[Tuple[object, Tuple[int,int]]]) -> List[Tuple[object, Tuple[int,int]]]:
    escolhidas = []
    indices_escolhidos: Set[int] = set()
    while len(escolhidas) < 3:
        try:
            print()
            mostrar_menu_selecao_naves(naves_all, selecionados=indices_escolhidos)
            escolha = input(f"Escolha a nave #{len(escolhidas)+1} pelo número (1-{len(naves_all)}): ").strip()
            idx = int(escolha)
            if idx < 1 or idx > len(naves_all):
                print("Índice fora do intervalo. Tente novamente.")
                continue
            if idx in indices_escolhidos:
                print("Já escolheu essa nave. Escolha outra.")
                continue
            nave_original = naves_all[idx-1][0]
            nd = nave_original.to_dict()
            if nd.get("class") == "NaveComExtra":
                nova = NaveComExtra.from_dict(nd)
            else:
                nova = NaveModelo.from_dict(nd)
            escolhidas.append((nova, None))
            indices_escolhidos.add(idx)
        except ValueError:
            print("Entrada inválida. Introduza o número da nave desejada.")
    return escolhidas

def posicionar_naves_aleatoriamente(naves_list: List[Tuple[object, Tuple[int,int]]], size: int) -> Dict[Tuple[int,int], object]:
    ocupadas = set()
    pos_map = {}
    for i, (nave, _) in enumerate(naves_list):
        if nave.energia <= 0:
            naves_list[i] = (nave, None)
            continue
        while True:
            r = random.randrange(size)
            c = random.randrange(size)
            if (r,c) not in ocupadas:
                ocupadas.add((r,c))
                pos_map[(r,c)] = nave
                naves_list[i] = (nave, (r,c))
                break
    return pos_map

def inicializar_jogo(size: int):
    naves_all = criar_naves_padroes()
    F.limpar_ecra()
    print("Antes de iniciar, escolha 3 naves do conjunto disponível.")
    escolhidas = escolher_3_naves(naves_all)
    pos_map = posicionar_naves_aleatoriamente(escolhidas, size)
    state = {
        "size": size,
        "naves": [ {"nave": entry[0].to_dict(), "pos": list(entry[1]) if entry[1] is not None else None} for entry in escolhidas ],
        "tiros": [],
        "tiros_acerto": [],
        "tiros_acerto_colors": [],
        "total_tiros": 0,
        "total_acertos": 0
    }
    naves_objs = []
    for entry in state["naves"]:
        nd = entry["nave"]
        pos = tuple(entry["pos"]) if entry["pos"] is not None else None
        if nd.get("class") == "NaveComExtra":
            obj = NaveComExtra.from_dict(nd)
        else:
            obj = NaveModelo.from_dict(nd)
        naves_objs.append({"obj": obj, "pos": pos})
    state["naves"] = naves_objs
    return state

def reconstruir_estado_carregado(d: dict):
    size = d.get("size", BOARD_SIZE)
    naves_serial = d.get("naves", [])
    naves = []
    for entry in naves_serial:
        nave_dict = entry.get("nave", {})
        pos = tuple(entry.get("pos")) if entry.get("pos") is not None else None
        if nave_dict.get("class") == "NaveComExtra":
            nave_obj = NaveComExtra.from_dict(nave_dict)
        else:
            nave_obj = NaveModelo.from_dict(nave_dict)
        naves.append({"obj": nave_obj, "pos": pos})
    tiros = [ tuple(t) for t in d.get("tiros", []) ]
    tiros_acerto_list = [ tuple(t) for t in d.get("tiros_acerto", []) ]
    tiros_acerto_colors = d.get("tiros_acerto_colors", [])
    if len(tiros_acerto_colors) != len(tiros_acerto_list):
        tiros_acerto_colors = tiros_acerto_colors + [None] * (len(tiros_acerto_list) - len(tiros_acerto_colors))
    state = {
        "size": size,
        "naves": naves,
        "tiros": tiros,
        "tiros_acerto": tiros_acerto_list,
        "tiros_acerto_colors": tiros_acerto_colors,
        "total_tiros": d.get("total_tiros", 0),
        "total_acertos": d.get("total_acertos", 0)
    }
    return state

def salvar_estado_para_arquivo(state: dict, filename: str = SAVE_FILENAME):
    try:
        serial = {
            "size": state["size"],
            "naves": [ {"nave": entry["obj"].to_dict(), "pos": list(entry["pos"]) if entry["pos"] is not None else None} for entry in state["naves"] ],
            "tiros": [ list(t) for t in state["tiros"] ],
            "tiros_acerto": [ list(t) for t in state["tiros_acerto"] ],
            "tiros_acerto_colors": list(state.get("tiros_acerto_colors", [])),
            "total_tiros": state["total_tiros"],
            "total_acertos": state["total_acertos"]
        }
        F.save_game(serial, filename)
        print("Jogo guardado com sucesso em", filename)
    except Exception as e:
        print("Erro ao guardar jogo:", e)

def carregar_estado_de_arquivo(filename: str = SAVE_FILENAME):
    try:
        d = F.load_game(filename)
        return reconstruir_estado_carregado(d)
    except FileNotFoundError:
        print("Ficheiro de save não encontrado.")
        return None
    except Exception as e:
        print("Erro ao carregar:", e)
        return None

def construir_pos_map(state: dict) -> Dict[Tuple[int,int], object]:
    pos_map = {}
    for entry in state["naves"]:
        if entry["pos"] is not None and entry["obj"].energia > 0:
            pos_map[tuple(entry["pos"])] = entry["obj"]
    return pos_map

def reposicionar_naves_apos_ronda(state: dict, size: int):
    vivos = [entry for entry in state["naves"] if entry["obj"].energia > 0]
    ocupadas = set()
    novas_pos = []
    for _ in vivos:
        while True:
            r = random.randrange(size)
            c = random.randrange(size)
            if (r,c) not in ocupadas:
                ocupadas.add((r,c))
                novas_pos.append((r,c))
                break
    j = 0
    for i, entry in enumerate(state["naves"]):
        if entry["obj"].energia > 0:
            state["naves"][i]["pos"] = novas_pos[j]
            j += 1
        else:
            state["naves"][i]["pos"] = None

def executar_game_loop():
    F.capa()
    while True:
        escolha = F.menu()
        if escolha == "1":
            state = inicializar_jogo(BOARD_SIZE)
            jogar(state)
        elif escolha == "2":
            loaded = carregar_estado_de_arquivo(SAVE_FILENAME)
            if loaded:
                jogar(loaded)
        elif escolha == "3":
            print("Para guardar o jogo deve primeiro estar em jogo e escolher a opção de guardar ao voltar ao menu.")
            input("Pressione Enter para voltar ao menu.")
        elif escolha == "4":
            print("Saindo...")
            break
        else:
            print("Opção inválida. Tente novamente.")

def jogar(state: dict):
    size = state.get("size", BOARD_SIZE)
    while True:
        F.limpar_ecra()
        pos_map = construir_pos_map(state)
        naves_vivas = [entry for entry in state["naves"] if entry["obj"].energia > 0]
        if len(naves_vivas) == 0:
            print("Todas as naves foram aniquiladas! Fim de jogo.")
            break
        if state["total_tiros"] >= MAX_TIRO:
            print(f"Total de tiros atingiu {MAX_TIRO}. Fim de jogo.")
            break

        print(f"Tiros totais até agora: {state['total_tiros']} | Acertos: {state['total_acertos']}")
        print("Vivas:")
        for entry in state["naves"]:
            if entry["obj"].energia > 0:
                obj = entry["obj"]
                obj.mostrar_dados()
        print()
        input("Pressione Enter para inserir os próximos 3 tiros (o ecrã será limpo)...")
        F.limpar_ecra()

        # recolher 3 tiros manualmente (cada tiro aceita 'r' para aleatório pontual)
        tiros_round: List[Tuple[int,int]] = []
        existentes = set(tuple(t) for t in state["tiros"])
        for i in range(3):
            t = F.ler_tiro_manual(size, existentes | set(tiros_round))
            tiros_round.append(t)
            existentes.add(t)

        # aplicar tiros (baseado nas posições ATUAIS pos_map)
        hits_this_round = []
        for t in tiros_round:
            state["tiros"].append(t)              # manter histórico para estatísticas/guarda
            state["total_tiros"] += 1
            if t in pos_map:
                nave = pos_map[t]
                prev = nave.energia
                nave.aplicar_perda()
                state["total_acertos"] += 1
                state["tiros_acerto"].append(t)           # histórico de acertos
                state.setdefault("tiros_acerto_colors", []).append(nave.cor)
                hits_this_round.append((t, nave.nome, prev, nave.energia, nave.cor))
            else:
                # miss -> nada para tiros_acerto
                pass

        # aplicar bónus de energia se for o caso
        if state["total_tiros"] == ENERGIA_BONUS_TIRO:
            print("BÓNUS: Cada nave recebe a sua energia_extra agora.")
            for entry in state["naves"]:
                obj = entry["obj"]
                if hasattr(obj, "adicionar_energia_extra"):
                    antes = obj.energia
                    obj.adicionar_energia_extra()
                    depois = obj.energia
                    print(f"{obj.nome}: {antes} -> {depois}")
            time.sleep(1)

        # Preparar representação para desenho combinado: usar somente tiros da ronda atual
        # IMPORTANT: NÃO reposicionar ainda — queremos desenhar o resultado correspondente às posições em que se deram os tiros
        pos_map = construir_pos_map(state)  # rebuild in case alguma nave morreu
        pos_naves_info = { pos: (entry["obj"].simbolo, entry["obj"].cor)
                           for entry in state["naves"] if entry["pos"] is not None and entry["obj"].energia > 0 for pos in [tuple(entry["pos"])] }

        tiros_acerto_colors_map = { hit[0]: hit[4] for hit in hits_this_round }  # {pos: cor}
        tab_combinado = desenhar_tabuleiro_combinado(size, pos_naves_info, tiros_round, tiros_acerto_colors_map)

        F.limpar_ecra()
        print("Tabuleiro - Naves (na posição do tiro) e Tiros desta ronda (X = acerto colorido):")
        print(tab_combinado)
        print()
        if hits_this_round:
            print("Acertos nesta ronda:")
            for (pos, nome, antes, depois, cor) in hits_this_round:
                print(f"Tiro em {pos} acertou {nome} (cor {cor}): Energia {antes} -> {depois}")
        else:
            print("Nenhum acerto nesta ronda.")

        print()
        print("Dados das naves:")
        for entry in state["naves"]:
            obj = entry["obj"]
            obj.mostrar_dados()

        total_tiros = state["total_tiros"]
        total_acertos = state["total_acertos"]
        eficacia = (total_acertos * 100.0 / total_tiros) if total_tiros > 0 else 0.0
        print()
        print(f"Total tiros: {total_tiros}")
        print(f"Total acertos: {total_acertos}")
        print(f"Eficácia: {eficacia:.2f}%")
        print()

        # Depois de apresentar os resultados da ronda, só então reposicionamos as naves
        # se o jogador decidir continuar.
        print("Opções:")
        print("1 - Continuar jogo (as naves serão reposicionadas depois de continuar)")
        print("2 - Voltar ao menu (pode guardar o jogo antes)")
        opc = input("Escolha (1-2): ").strip()
        if opc == "1":
            # reposicionar para próxima ronda
            reposicionar_naves_apos_ronda(state, size)
            continue
        else:
            quer_guardar = input("Deseja guardar o jogo antes de voltar ao menu? (s/n): ").strip().lower()
            if quer_guardar == "s":
                salvar_estado_para_arquivo(state, SAVE_FILENAME)
                input("Pressione Enter para voltar ao menu.")
            return  # volta ao menu principal

if __name__ == "__main__":
    executar_game_loop()