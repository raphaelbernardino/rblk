from novo.regras.regras_util import existe_alvo_entre_as_portas, inverte_controles


def pode_eliminar_not_duplicado(c, i, j):
    """
    Verifica se pode aplicar a regra 2.

    def: Se em determinada linha <i> do circuito <c> existir um par de portas NOT, essas podem ser
    eliminados invertendo as conexões de controle na linha <i> de todas as portas intermediárias, desde
    que não existam alvos nas portas intermediárias na linha <i>.

    :param c: Circuito a ser analisado
    :param i: <i>-ésima porta do circuito C
    :param j: <j>-ésima porta do circuito C
    :return: A regra pode ser aplicada?
    """
    if len(c) < 2:
        return False

    # print('T', len(c), i, j)
    pg = c.portas[i]
    ph = c.portas[j]

    # se porta G não é NOT, não pode aplicar a regra
    if not pg.eh_porta_not():
        return False

    # se porta H não é NOT, não pode aplicar a regra
    if not ph.eh_porta_not():
        return False

    # se porta G não tem o mesmo alvo da porta H, não pode aplicar
    if pg.obtem_alvos() != ph.obtem_alvos():
        return False

    # se existe um alvo entre as linhas I e J, não pode aplicar
    if existe_alvo_entre_as_portas(c, i, j):
        return False

    # porta eliminada
    return True


def busca_proxima_porta_not(circuito, k, linha=None):
    while k < len(circuito.portas):
        p1 = circuito.portas[k]
        linha_alvo = p1.obtem_alvos()[0].linha

        if p1.eh_porta_not() and linha is None:
            # print("L2",  linha, p1)
            break
        elif p1.eh_porta_not() and linha is not None and linha == linha_alvo:
            # print("L3", linha, linha_alvo, p1)
            break
        else:
            # print("L4", linha, linha_alvo, p1)
            pass

        # busca a próxima porta
        k += 1

    return k


def aplica_eliminacao_de_not_duplicado(circuito):
    """
    Tenta aplicar a regra 2 que elimina NOTs duplicados.

    :param circuito: Circuito a ser analisado
    :return: Circuito reduzido
    """
    tamanho_original = circuito.gc

    # se o circuito tem menos de 2 portas, então chegou ao fim
    chegou_ao_fim = circuito.gc < 2

    g = 0
    while not chegou_ao_fim:
        # busca as duas primeiras portas NOT
        g = busca_proxima_porta_not(circuito, g)
        if g >= circuito.gc:
            # chegou_ao_fim = True
            break
        linha = circuito.portas[g].obtem_alvos()[0].linha

        h = busca_proxima_porta_not(circuito, g + 1, linha)
        if h >= circuito.gc:
            g += 1
            continue

        # print("G", g, "H", h)

        if pode_eliminar_not_duplicado(circuito, g, h):
            # inverte os controles das portas que estão entre as posições I e J do circuito
            linha_a_ser_invertida = circuito.portas[g].alvos.linha
            inverte_controles(circuito, g, h, linha_a_ser_invertida)

            circuito.apaga_porta_por_indice(g)
            circuito.apaga_porta_por_indice(h - 1)

            # volta para o inicio
            g = 0
        else:
            g += 1

    # faz mais uma passada no caso do tamanho ter reduzido
    if tamanho_original > circuito.gc:
        aplica_eliminacao_de_not_duplicado(circuito)
