from novo.circuitos.controle import Controle
from novo.circuitos.toffoli import Toffoli


def possui_alvo_nos_controles(alvos, controles):
    """
    Verifica em cada linha de controle se há uma linha de alvo.

    :param alvos: Uma lista de alvos do tipo Alvo.
    :param controles: Uma lista de controles do tipo Controle.
    :return: Um valor booleano indicando se há em alguma linha de alvo algum controle.
    """
    for ctrl in controles:
        if type(alvos) is list:
            for alvo in alvos:
                if alvo.linha == ctrl.linha:
                    return True
        else:
            if alvos.linha == ctrl.linha:
                return True
    return False


def obtem_quantidade_de_controles_distintos_na_mesma_linha(controles_a, controles_b):
    """
    Dados dois controles, determine a quantidade de controles distintos na mesma linha.

    :param controles_a: Os controles da porta A.
    :param controles_b: Os controles da porta B.
    :return: A quantidade de controles distintos que estão na mesma linha.
    """
    distintos = 0

    for ctrl_a in controles_a:
        for ctrl_b in controles_b:
            if ctrl_a.linha == ctrl_b.linha and ctrl_a.possui_sinal_inverso(ctrl_b):
                distintos += 1

    return distintos


# def obtem_quantidade_de_controles_iguais_na_mesma_linha(controles_a, controles_b):
#     """ Retorna a quantidade de controles iguais que existem em ambas as portas. """
#     iguais = 0
#
#     for ctrl_a in controles_a:
#         for ctrl_b in controles_b:
#             if ctrl_a.linha == ctrl_b.linha:
#                 iguais += 1
#
#     return iguais
#
#
# def todos_controles_sao_iguais(ctrls_g, ctrls_h):
#     return obtem_quantidade_de_controles_iguais_na_mesma_linha(ctrls_g, ctrls_h) == len(ctrls_g)


def existe_alvo_entre_as_portas(c, g, h):
    """
    Existe alvo <a> entre as linhas <g> e <h> do circuito <c> ?

    :param c: Circuito a ser analisado
    :param g: Posição da porta G no circuito C
    :param h: Posição da porta H no circuito C
    :return: Existe alvo entre <g> e <h>?
    """
    a = c.portas[g].obtem_alvos()

    for k in range(g + 1, h):
        pk = c.portas[k]

        if pk.obtem_alvos() == a:
            return True

    return False


def inverte_controles(c, g, h, linhas):
    """
    Inverte o controle entre as <g>-ésima e <h>-ésima portas na linha <ctrl> do circuito <c>

    :param c: Circuito a ser analisado
    :param g: Porta G do circuito C
    :param h: Porta H do circuito C
    :param linhas: Linha a ser analisada
    :return:
    """

    if linhas is not list:
        linhas = [linhas]

    for k in range(g, h):
        c.portas[k].inverte_controle_nas_linhas(linhas)


def funde_portas(pg, ph):
    """
    Funde duas portas PG e PH usando as regras de fusão (regra 3).

    :param pg: Porta G.
    :param ph: Porta H.
    :return: Fusão das duas portas G e H em uma nova porta K.
    """
    diff = pg.diferenca_entre_controles(ph)
    controles_k = list()

    if 2 < len(diff) < 1:
        # se tem menos de 1, ou mais de 2, linhas de controles diferentes, não tem como fundir
        return None

    if len(diff) == 1:
        d = diff[0]

        controles_k += inverte_sinal_dos_controles(d, pg)
        controles_k += inverte_sinal_dos_controles(d, ph)

    elif len(diff) == 2:
        d1, d2 = diff

        for ctrl in pg.controles:
            if ctrl != d1 and ctrl != d2:
                um_controle = Controle(ctrl.linha, ctrl.sinal)
                controles_k.append(um_controle)

    controles_k = set(controles_k)
    pk = Toffoli(pg.alvos, controles_k)
    return pk


def inverte_sinal_dos_controles(c, p):
    """
    Inverte o sinal de todos os controles da porta se o controle é igual a C.

    :param c: Um controle Controle C
    :param p: Uma Porta P
    :return: Os controles invertidos
    """
    ctrls = list()

    for ctrl in p.controles:
        if ctrl == c:
            ctrl_invertido = Controle(ctrl.linha, ctrl.sinal)
            ctrl_invertido.inverte_sinal()
            ctrls.append(ctrl_invertido)
        else:
            ctrls.append(ctrl)

    return ctrls
