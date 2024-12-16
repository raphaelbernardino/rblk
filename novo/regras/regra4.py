from novo.regras.regras_util import possui_alvo_nos_controles, obtem_quantidade_de_controles_distintos_na_mesma_linha


def pode_aplicar_swap(pg, ph):
    """
    Verifica se pode aplicar a regra 4 (SWAP).

    def: Duas portas Toffoli generalizadas consecutivas G e H podem ser comutadas se uma das condições ocorrer:
    (1) a linha de alvo de uma porta não é linha de controle da outra;
    (2) duas portas tem uma conexão de controle reverso em uma linha, e são idênticas nas demais linhas;

    :param pg: Uma porta G.
    :param ph: Uma porta H.
    :return: Pode aplicar a regra 4?
    """
    alvos_pg = pg.alvos
    ctrls_pg = pg.controles

    alvos_ph = ph.alvos
    ctrls_ph = ph.controles

    # Caso 1
    r1 = not possui_alvo_nos_controles(alvos_pg, ctrls_ph)
    r2 = not possui_alvo_nos_controles(alvos_ph, ctrls_pg)
    if r1 and r2:
        return True

    # Caso 2
    qtd_ctrl_diff = obtem_quantidade_de_controles_distintos_na_mesma_linha(ctrls_pg, ctrls_ph)
    return qtd_ctrl_diff == 1


def aplica_swap(pg, ph):
    """
    Aplica a regra 4 (SWAP) que comuta portas consecutivas.

    :param pg: Uma porta G.
    :param ph: Uma porta H.
    :return: Retorna a porta H e G.
    """
    if not pode_aplicar_swap(pg, ph):
        print('aplica_swap :: swap não aplicado')
        return pg, ph

    return ph, pg


def aplica_swap_no_circuito(circuito):
    """
    Tenta aplicar a regra 4 que realiza SWAPs no circuito.

    :param circuito: Circuito a ser analisado
    :return: Circuito modificado utilizando SWAPs
    """
    # se o circuito tem menos de 2 portas, então chegou ao fim
    chegou_ao_fim = circuito.gc < 2

    i = 0
    while not chegou_ao_fim:
        pg = circuito.portas[i]
        ph = circuito.portas[i + 1]

        if pode_aplicar_swap(pg, ph):
            pg, ph = aplica_swap(pg, ph)

            circuito.portas[i] = pg
            circuito.portas[i + 1] = ph

        # verifica a próxima porta
        i += 1

        if i == circuito.gc - 1:
            chegou_ao_fim = True
