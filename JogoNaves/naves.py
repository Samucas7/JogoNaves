"""
naves.py
Definição das classes NaveModelo e NaveComExtra e mapeamento ANSI para cores.
"""

# Mapeamento de cores ANSI a nível de módulo (usado para colorir saídas)
ANSI_CORES = {
    "preto": "\u001b[30m",
    "vermelho": "\u001b[31m",
    "verde": "\u001b[32m",
    "amarelo": "\u001b[33m",
    "azul": "\u001b[34m",
    "magenta": "\u001b[35m",
    "ciano": "\u001b[36m",
    "branco": "\u001b[37m",
}
ANSI_RESET = "\u001b[0m"


class NaveModelo:
    MAX_ENERGIA = 100

    def __init__(self, nome: str = "", cor: str = "", energia: int = 100, perderEnergia: int = 0, simbolo: str = ""):
        self.nome = nome
        self.cor = cor
        # garante energia entre 0 e MAX_ENERGIA
        self.energia = max(0, min(self.MAX_ENERGIA, int(energia)))
        self.perderEnergia = int(perderEnergia)
        self.simbolo = simbolo

    def aplicar_perda(self) -> int:
        """
        Subtrai self.perderEnergia da energia atual (mínimo 0).
        Retorna a energia atualizada.
        """
        self.energia = max(0, self.energia - self.perderEnergia)
        return self.energia

    def obter_energia_atual(self) -> int:
        """Retorna a energia atual da nave."""
        return self.energia

    def mostrar_dados(self):
        """
        Mostra nome, energia atual e símbolo com a cor definida.
        Garante que termina com ANSI_RESET para evitar vazamento de cor.
        """
        codigo = ANSI_CORES.get((self.cor or "").lower(), "")
        # sempre incluir reset (mesmo que codigo seja "")
        texto = f"Nome: {self.nome} | Energia: {self.energia} | Símbolo: {self.simbolo}"
        print(f"{codigo}{texto}{ANSI_RESET}")

    def to_dict(self) -> dict:
        """Serialização simples para guardar em ficheiro."""
        return {
            "class": "NaveModelo",
            "nome": self.nome,
            "cor": self.cor,
            "energia": self.energia,
            "perderEnergia": self.perderEnergia,
            "simbolo": self.simbolo
        }

    @classmethod
    def from_dict(cls, d: dict):
        return cls(nome=d.get("nome", ""), cor=d.get("cor", ""), energia=d.get("energia", 100),
                   perderEnergia=d.get("perderEnergia", 0), simbolo=d.get("simbolo", ""))


class NaveComExtra(NaveModelo):
    def __init__(self, nome: str = "", cor: str = "", energia: int = 100, perderEnergia: int = 0, simbolo: str = "", energia_extra: int = 0):
        super().__init__(nome=nome, cor=cor, energia=energia, perderEnergia=perderEnergia, simbolo=simbolo)
        self.energia_extra = int(energia_extra)

    def mostrar_dados(self):
        """
        Mostra nome, energia atual e símbolo com a cor definida.
        Garante que termina com ANSI_RESET para evitar vazamento de cor.
        """
        codigo = ANSI_CORES.get((self.cor or "").lower(), "")
        texto = f"Nome: {self.nome} | Energia: {self.energia} | Símbolo: {self.simbolo}"
        print(f"{codigo}{texto}{ANSI_RESET}")

    def adicionar_energia_extra(self) -> int:
        """
        Adiciona energia_extra à energia atual sem ultrapassar MAX_ENERGIA.
        Retorna a energia resultante.
        """
        self.energia = min(self.MAX_ENERGIA, self.energia + self.energia_extra)
        return self.energia

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["class"] = "NaveComExtra"
        d["energia_extra"] = self.energia_extra
        return d

    @classmethod
    def from_dict(cls, d: dict):
        return cls(nome=d.get("nome", ""), cor=d.get("cor", ""), energia=d.get("energia", 100),
                   perderEnergia=d.get("perderEnergia", 0), simbolo=d.get("simbolo", ""), energia_extra=d.get("energia_extra", 0))