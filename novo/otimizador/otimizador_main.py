from novo.logs.logging_utils import create_logger
from novo.otimizador.analisador_matriz_hamming.analisador_hamming import otimiza_com_circuito_minimo
from novo.otimizador.otimizador_de_circuitos import reorganiza_usando_swaps3
from novo.otimizador.otimizador_reed import executa_pos_sintese
from novo.otimizador.otimizador_util import realiza_leitura_tfc, verifica_otimizacao
from novo.regras import aplica_eliminacao_de_not_duplicado, aplica_eliminacao_de_portas_iguais, aplica_merge

logger = create_logger('otimizador_main', level='DEBUG')


def executa_otimos(circ):
    if isinstance(circ, str):
        circ = realiza_leitura_tfc(circ)

    # reorganiza o circuito para reduzir dist. hamming (usando SWAPs e MOVEs), e
    circ = reorganiza_usando_swaps3(circ)
    logger.info(f'Circuito após reorganizar com SWAP/MOVE:\n{circ}')

    # aplica circuitos otimos (janela com menor dist. hamming)
    circ = otimiza_com_circuito_minimo(circ)
    logger.info(f'Circuito após aplicar circuitos ótimos:\n{circ}')

    return circ


def executa_regras(circ):
    if isinstance(circ, str):
        circ = realiza_leitura_tfc(circ)

    # aplica a regra de eliminacao de portas not
    aplica_eliminacao_de_not_duplicado(circ)
    logger.info(f'Circuito após aplicar regra 2 (elim. NOT duplicados):\n{circ}')

    # aplica a regra de eliminacao de portas iguais
    aplica_eliminacao_de_portas_iguais(circ)
    logger.info(f'Circuito após aplicar regra 1 (elim. portas duplicadas):\n{circ}')

    # aplica a regra merge para juntar portas similares
    aplica_merge(circ)
    logger.info(f'Circuito após aplicar regra 3 (merge):\n{circ}')

    return circ


def executa_reed(circ):
    if isinstance(circ, str):
        circ = realiza_leitura_tfc(circ)

    # reorganiza circuito para alvos estarem na mesma linha, e
    # aplica reed-muller modo pós-sintese (janela com mesmo alvo)
    circ = executa_pos_sintese(circ)
    logger.info(f'Circuito após aplicar pós-sintese com RM:\n{circ}')

    return circ


def executa_algoritmo_novo(nome_tfc: str):
    # realiza leitura do TFC
    circ = realiza_leitura_tfc(nome_tfc)
    logger.info(f'Circuito Original:\n{circ}')

    # cria uma copia do circuito original
    circ_original = circ.obtem_copia()

    # otimiza
    circ = executa_regras(circ)
    circ = executa_otimos(circ)
    circ = executa_reed(circ)
    circ = executa_otimos(circ)
    logger.info(f'Circuito Final:\n{circ}')

    # verifica se a otimizacao foi feita corretamente
    verifica_otimizacao(circ_original, circ)

    return circ
