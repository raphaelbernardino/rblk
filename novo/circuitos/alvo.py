class Alvo:
    def __init__(self, linha, mapa=None):
        self.linha_original = int(linha)

        if mapa is None:
            self.linha = int(linha)
        else:
            if linha >= len(mapa):
                self.linha = linha
            else:
                self.linha = int(mapa[linha])

        if self.linha < 0:
            raise Exception('Alvo inválido! Linha negativa.')

    def modifica_linha(self, modificacao: int):
        """
        Modifica a linha atual. Para aumentar a linha informe um valor positivo, e para diminuir, um valor negativo.

        modificacao: int
        """
        self.linha = self.linha + modificacao

    def remapeia(self, mapa):
        self.linha = mapa[self.linha]

    def __repr__(self):
        return f'b{self.linha}'

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        if self.linha != other.linha:
            return False

        return True

    def __lt__(self, other):
        if not isinstance(other, self.__class__):
            raise Exception('Não é possível comparar Alvo com outro tipo.')

        return self.linha < other.linha

    def __hash__(self):
        return id(self.linha) * hash(self.linha + 1)
