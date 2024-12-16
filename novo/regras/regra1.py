def pode_aplicar_eliminacao_de_portas_iguais(pg, ph):
    """
    Verifica se pode aplicar a regra 1.

    def: Duas portas Toffoli generalizadas consecutivas G e H com mesmos controles e alvos se anulam.

    :param pg: Porta G
    :param ph: Porta H
    :return: A regra pode ser aplicada?
    """

    return pg == ph


def aplica_eliminacao_de_portas_iguais(circuito):
    """
    Tenta aplicar a regra 1 que elimina duas portas iguais e consecutivas.

    :param circuito: Circuito a ser analisado
    :return: Circuito reduzido
    """

    tamanho_original = circuito.gc
    i = 0
    while i < circuito.gc - 1:
        pg = circuito.portas[i]
        ph = circuito.portas[i + 1]

        if pode_aplicar_eliminacao_de_portas_iguais(pg, ph):
            circuito.apaga_porta_por_indice(i)
            circuito.apaga_porta_por_indice(i)
        else:
            # verifica a próxima porta
            i += 1

    # faz mais uma passada no caso do tamanho ter reduzido
    if tamanho_original > circuito.gc:
        aplica_eliminacao_de_portas_iguais(circuito)
