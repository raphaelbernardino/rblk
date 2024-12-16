from novo.circuitos.circuito import Circuito
from novo.logs.logging_utils import create_logger
from novo.otimizador.otimizador_de_circuitos import reorganiza_circuito, reduz_circuito_usando_regras_e_circuitos_otimos
from novo.otimizador.otimizador_util import realiza_leitura_tfc

logger = create_logger('benchmark_aleatorio_util', level='DEBUG')


def reduz_circuitos(circ: Circuito, reorganiza: bool = True,
                    aplica_regras: bool = True, aplica_otimos: bool = True,
                    aplica_reed: bool = True):
    # reorganiza o circuito usando SWAPs
    if reorganiza:
        circ = reorganiza_circuito(circ)

    # otimiza o circuito
    circ = reduz_circuito_usando_regras_e_circuitos_otimos(circ,
                                                           usa_regras=aplica_regras,
                                                           usa_otimos=aplica_otimos,
                                                           usa_reed=aplica_reed)
    logger.info(f'Circuito Otimizado:\n{circ}')

    return circ


def le_arquivo_e_reduz_circuitos(nome_tfc: str, reorganiza: bool = True,
                                 aplica_regras: bool = True, aplica_otimos: bool = True, aplica_reed: bool = True):
    circ = realiza_leitura_tfc(nome_tfc)
    logger.info(f'Circuito Original:\n{circ}')

    circ = reduz_circuitos(circ, reorganiza=reorganiza,
                           aplica_regras=aplica_regras, aplica_otimos=aplica_otimos, aplica_reed=aplica_reed)

    return circ
