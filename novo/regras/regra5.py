from novo.regras.regras_util import possui_alvo_nos_controles


def pode_aplicar_move(pg, ph):
    """
    Verifica se pode aplicar a regra 5 (MOVE).

    def: Duas portas Toffoli generalizadas G e H podem ser movimentadas se ambas condições ocorrerem:
    (1) o alvo da porta G está em uma linha onde a porta H tem uma conexão de controle;
    (2) todas as linhas na porta G com uma conexão de controle também tem uma conexão de controle na
    porta H, e em todas as linhas nas quais ambas têm conexão de controle, estas são as mesmas.

    :param pg: Porta G.
    :param ph: Porta H.
    :return: A regra pode ser aplicada?
    """
    alvo_pg = pg.alvos
    ctrls_pg = pg.controles
    ctrls_ph = ph.controles

    # Condição 1
    if not possui_alvo_nos_controles(alvo_pg, ctrls_ph):
        return False

    # Condição 2.
    for ctrl_g in ctrls_pg:
        if ctrl_g not in ctrls_ph:
            return False

    # se ambas condições são atendidas, pode aplicar
    return True


def aplica_move(pg, ph):
    """
    Aplica a regra 5 (MOVE) que comuta portas consecutivas invertendo os controles nas linhas de alvo. Ao ser
    movimentada inverte-se a conexão de controle da porta H posicionada na mesma linha que o alvo da porta G.

    :param pg: Uma porta G.
    :param ph: Uma porta H.
    :return: Retorna a porta H e G com a conexão de controle invertida nas linhas dos alvos.
    """
    if not pode_aplicar_move(pg, ph):
        print('aplica_move :: move não aplicado')
        return pg, ph

    # inverte o controle de H nas linhas onde os alvos de G estão localizados
    linhas_alvo = [alvo.linha for alvo in pg.obtem_alvos()]
    ph.inverte_controle_nas_linhas(linhas_alvo)

    # comuta a porta G por H
    return ph, pg


def aplica_move_no_circuito(circuito):
    """
    Tenta aplicar a regra 5 que realiza MOVEs no circuito.

    :param circuito: Circuito a ser analisado
    :return: Circuito modificado utilizando MOVEs
    """
    # se o circuito tem menos de 2 portas, então chegou ao fim
    chegou_ao_fim = circuito.gc < 2

    i = 0
    while not chegou_ao_fim:
        pg = circuito.portas[i]
        ph = circuito.portas[i + 1]

        if pode_aplicar_move(pg, ph):
            pg, ph = aplica_move(pg, ph)

            circuito.portas[i] = pg
            circuito.portas[i + 1] = ph

        # verifica a próxima porta
        i += 1

        if i == circuito.gc - 1:
            chegou_ao_fim = True
