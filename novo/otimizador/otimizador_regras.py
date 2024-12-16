from novo.regras.regra4 import pode_aplicar_swap, aplica_swap
from novo.regras.regra5 import pode_aplicar_move, aplica_move


def aplica_swap_ou_move(pg, ph):
    """
        Tenta aplicar a regra 4 (SWAP) ou a regra 5 (MOVE), dependendo da situação.
    :param pg: Uma porta G do tipo Toffoli ou Fredkin.
    :param ph: Uma porta H do tipo Toffoli ou Fredkin.
    :return: As portas modificadas com SWAP/MOVE.
    """

    if pode_aplicar_swap(pg, ph):
        pg, ph = aplica_swap(pg, ph)

    elif pode_aplicar_move(pg, ph):
        pg, ph = aplica_move(pg, ph)

    return pg, ph
