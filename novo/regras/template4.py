from novo.circuitos.states import States


def distancia_de_hamming(pg, ph):
    ctrls_pg = set(pg.controles)
    ctrls_ph = set(ph.controles)
    ctrls_diff = ctrls_pg.symmetric_difference(ctrls_ph)
    # print(f'{ctrls_diff=}')

    linhas_diff = set()
    for ctrl in ctrls_diff:
        linha = [ctrl.linha]
        linhas_diff = linhas_diff.union(linha)

    return len(linhas_diff), linhas_diff


def obtem_linha_dos_controles(ctrls):
    linhas = set()

    for ctrl in ctrls:
        linha = [ctrl.linha]
        linhas = linhas.union(linha)

    return linhas


def complementa_portas(pg, ph):
    novas_portas = list()

    ctrls_pg = sorted(set(pg.controles))
    ctrls_ph = sorted(set(ph.controles))

    # ctrls = ctrls_pg.union(ctrls_ph)
    # print(f'{ctrls=}')
    # linhas_controles = obtem_linha_dos_controles(ctrls)
    # print(f'{linhas_controles=}')

    for ctrl1 in ctrls_pg:
        for ctrl2 in ctrls_ph:
            if ctrl1.linha == ctrl2.linha:
                print(f'{ctrl1=} \t {ctrl2=}')

                if ctrl1.sinal == States.ctrl_positivo and ctrl2.sinal == States.ctrl_negativo:
                    ctrl1.sinal = States.ctrl_ausente

                # if ctrl2.sinal == States.ctrl_positivo and ctrl1.sinal == States.ctrl_negativo:
                #     ctrl2.sinal = States.ctrl_ausente

                if ctrl1.sinal == States.ctrl_negativo and ctrl2.sinal == States.ctrl_positivo:
                    ctrl1.sinal = States.ctrl_ausente

                # if ctrl2.sinal == States.ctrl_negativo and ctrl1.sinal == States.ctrl_positivo:
                #     ctrl2.sinal = States.ctrl_ausente

    return novas_portas


def pode_realizar_template4(pg, ph):
    """
    ToDo.

    :param pg: Porta G
    :param ph: Porta H
    :return: A regra pode ser aplicada?
    """
    distancia, linhas_distintas = distancia_de_hamming(pg, ph)
    return 2 <= distancia <= 3


def aplica_template4(circuito):
    """
    Tenta aplicar a regra 3 que funde portas adjacentes.

    :param circuito: Circuito a ser analisado
    :return: Circuito reduzido
    """
    tamanho_circuito = len(circuito)

    # se o circuito tem menos de 2 portas, então chegou ao fim
    chegou_ao_fim = tamanho_circuito < 2

    i = 0
    while not chegou_ao_fim:
        pg = circuito.portas[i]
        ph = circuito.portas[i + 1]

        if pode_realizar_template4(pg, ph):
            # complementa as portas G e H
            novas_portas = complementa_portas(pg, ph)

            for _ in range(len(novas_portas)):
                circuito.apaga_porta_por_indice(i)

            # insere as novas portas na posição
            for k in range(len(novas_portas)):
                circuito.insere_porta_por_indice(i + k, novas_portas[k])

            # atualiza a qtd. de portas
            tamanho_circuito = len(circuito)
        else:
            # verifica a próxima porta
            i += 1

        if i == tamanho_circuito - 1:
            chegou_ao_fim = True
