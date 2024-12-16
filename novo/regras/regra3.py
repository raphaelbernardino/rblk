from novo.regras.regras_util import funde_portas


def pode_realizar_merge(pg, ph):
    """
    Verifica se pode aplicar a regra 3.

    def: Duas portas Toffoli generalizadas adjacentes consecutivas G e H podem ser fundidas. A porta resultante
    terá a conexão de controle que não aparece na linha em que diferem.

    :param pg: Porta G
    :param ph: Porta H
    :return: A regra pode ser aplicada?
    """
    return pg.eh_adjacente(ph)


def aplica_merge(circuito):
    """
    Tenta aplicar a regra 3 que funde portas adjacentes.

    :param circuito: Circuito a ser analisado
    :return: Circuito reduzido
    """
    # se o circuito tem menos de 2 portas, então chegou ao fim
    chegou_ao_fim = circuito.gc < 2

    i = 0
    while not chegou_ao_fim:
        pg = circuito.portas[i]
        ph = circuito.portas[i + 1]

        if pode_realizar_merge(pg, ph):
            # funde as portas G e H
            porta_nova = funde_portas(pg, ph)

            circuito.apaga_porta_por_indice(i)
            circuito.apaga_porta_por_indice(i)

            # insere a nova porta na posição
            circuito.insere_porta_por_indice(i, porta_nova)
        else:
            # verifica a próxima porta
            i += 1

        if i == circuito.gc - 1:
            chegou_ao_fim = True
