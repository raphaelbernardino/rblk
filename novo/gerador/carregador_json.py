from novo.logs.logging_utils import create_logger
from novo.otimizador.otimizador_util import carrega_arquivo_permutacao

logger = create_logger(name='carregador_json', level='DEBUG')

PERMUTACOES = dict()


def preload_permutacoes(qtd_bits_min: int = 1, qtd_bits_max: int = 3):
    if len(PERMUTACOES) < 1:
        logger.debug('carregando arquivo de permutações...')
        for qtd_bits in range(qtd_bits_min, qtd_bits_max + 1):
            perms = carrega_arquivo_permutacao(qtd_bits)

            # for k, v in perms.items():
            #     print(f'Permutações {qtd_bits}:: Permutação {k}:\n{v}')

            PERMUTACOES.update(perms)
        logger.debug('carregado!')

    return PERMUTACOES
