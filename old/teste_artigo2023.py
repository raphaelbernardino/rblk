"""
Automatic generation of Grover quantum oracles for arbitrary data structures.
Raphael Seidel et al. 2023 Quantum Sci. Technol. 8 025003
"""

import random

from novo.logs.logging_utils import create_logger
from novo.otimizador.otimizador_reed import executa_sintese, executa_pos_sintese

logger = create_logger(name='teste_artigo', level='INFO')


def gera_tabela_verdade(k):
    """
    Gera uma tabela verdade contendo 2**k linhas e k colunas.

    @param k: A quantidade de bits a ser utilizada na tabela-verdade.
    @return: Uma lista contendo 0s e 1s em cada coluna, e k elementos por linha.
    """
    tabela = list()

    for i in range(2 ** k):
        r = [random.randint(0, 1) for _ in range(k)]
        tabela.append(r)

    return tabela


def gera_experimentos(qtd_casos_por_experimento=30, experimento_inicial=2, experimento_final=10):
    """
    Gera as tabelas verdades a serem utilizadas nos experimentos. Cada experimento é retornado por vez, diminuindo o uso
    de memória necessário.

    @param qtd_casos_por_experimento: A quantidade de casos (tabelas-verdade) por experimento.
    @param experimento_inicial: O número inicial do experimento.
    @param experimento_final: O número final do experimento.
    @return: Retorna de forma iterativa o conjunto de dados de cada experimento.
    """
    for k in range(experimento_inicial, experimento_final + 1):
        dados_experimento = list()

        for _ in range(qtd_casos_por_experimento):
            dado = gera_tabela_verdade(k)
            dados_experimento.append(dado)

        yield dados_experimento


def realiza_teste(i, experimento):
    """
    Realiza o teste do i-ésimo experimento.

    @param i: O número identificador do experimento a ser realizado, e também a quantidade de bits a ser utilizada
    no experimento.
    @param experimento: O conjunto de dados do experimento a ser realizado.
    @return:
    """
    logger.debug(f'Experimento #{i}:')

    custo_total_cnot = custo_total_qc = 0

    #### GAMBIARRA
    # nome_arquivo_sintese = 'circuito-sintese.tfc'
    # nome_arquivo_pos = 'circuito-pos.tfc'
    #### GAMBIARRA

    for d, dados in enumerate(experimento):
        logger.debug(f'\tDados #{d + 1} (n={i}): {dados}')

        circuito_sintese = executa_sintese(n=i, tabela_saida=dados)
        logger.debug(f'Circuito gerado (sintese):\n{circuito_sintese}')

        # circuito_sintese.salva_em_arquivo(nome_arquivo_sintese)
        # testa_reverso(nome_arquivo_sintese, arquivo_destino=nome_arquivo_pos, base_diretorio='testes-artigo')
        # circuito = realiza_leitura_tfc(nome_arquivo_pos)

        circuito = executa_pos_sintese(circuito_sintese)
        logger.debug(f'Circuito gerado (pos-sintese):\n{circuito}')

        custo_cnot = circuito.custo_cnot()
        custo_quantico = circuito.custo_quantico()
        logger.debug(f'\tCusto CNOT: {custo_cnot} :: Custo Quântico: {custo_quantico}')

        custo_total_cnot += custo_cnot
        custo_total_qc += custo_quantico

        # espera um tempo para ler a tela
        # logger.debug(f'Sleeping...')
        # sleep(10*1000)

    custo_medio_cnot = custo_total_cnot / len(experimento)
    custo_medio_qc = custo_total_qc / len(experimento)

    logger.info(
        f'k={i} :: datasize={2 ** i} :: Custo CNOT médio: {custo_medio_cnot:,.2f} :: Custo Quântico médio: {custo_medio_qc:,.2f}')
    logger.debug('-' * 15)


def main():
    # define a seed para reprodutibilidade
    random.seed(10)

    # gera os experimentos
    i = 2
    experimentos = gera_experimentos(experimento_inicial=i, experimento_final=5, qtd_casos_por_experimento=3000)

    # realiza experimentos
    while experimento := next(experimentos, False):
        realiza_teste(i, experimento)
        i += 1


if __name__ == '__main__':
    main()
