import copy
from typing import List

import numpy as np

from novo.circuitos.circuito import Circuito
from novo.circuitos.toffoli import Toffoli
from novo.gerador.carregador_json import preload_permutacoes
from novo.logs.logging_utils import create_logger
from novo.otimizador.otimizador_util import realiza_leitura_tfc

logger = create_logger(name='analisador_hamming', level='INFO')


def monta_vetor(porta: Toffoli, qtd_bits: int):
    """
    Recebe uma porta e retorna um vetor numerado com os valores de identificação, conforme tabela abaixo:

        0 - controle ausente/vazio
        1 - controle positivo
        2 - controle negativo
        3 - alvo

    Exemplo:
        Porta T3 b0,b1,b2 --> vetor associado: [1, 1, 3]
        Porta T4 b0,b1',b2,b3 --> vetor associado: [1, 2, 1, 3]
        Porta T2 b1,b0 --> vetor associado: [3, 1]

    @param porta:
    @param qtd_bits:
    @return:
    """
    # obtem a quantidade de linhas usadas pela porta
    tamanho_porta = len(porta)

    if qtd_bits < tamanho_porta:
        raise Exception("A quantidade de bits informada difere da quantidade de bits usada pela porta.")

    # gera o vetor
    vetor = [0] * qtd_bits

    # obtem os alvos e controles da porta
    alvo = porta.alvos
    controles = porta.controles

    # extrai a linha do alvo e preenche o vetor com a posicao do alvo
    linha_alvo = alvo.linha
    vetor[linha_alvo] = 3

    # extrai as linhas dos controles e preenche o vetor
    for ctrl in controles:
        linha_ctrl = ctrl.linha

        if ctrl.eh_sinal_positivo():
            vetor[linha_ctrl] = 1
        else:
            vetor[linha_ctrl] = 2

    return vetor


def compara_distancia_entre_vetores(um_vetor: List[int], outro_vetor: List[int]):
    distancia = 0

    if len(um_vetor) != len(outro_vetor):
        raise Exception('A quantidade de bits de um vetor difere da quantidade de bits do outro vetor.')

    # cria uma cópia do primeiro vetor
    vetor_distancia = um_vetor[:]

    # analisa a distância entre os vetores
    for i in range(len(um_vetor)):
        if um_vetor[i] != outro_vetor[i]:
            distancia += 1

            # marca como uma posição diferente "X"
            vetor_distancia[i] = -1

    return distancia, vetor_distancia


def gera_matriz_de_distancias(circuito: Circuito):
    # obtem a quantidade de portas
    qtd_portas = len(circuito)

    # cria uma matriz zerada com dimensoes qtd_portas x qtd_portas
    dimensoes = (qtd_portas, qtd_portas)
    matriz = np.zeros(dimensoes, dtype=int)

    return matriz


# def percorre_portas(portas, delta=1):
#     for i in range(len(portas) - delta):
#         uma_porta = portas[i]
#         outra_porta = portas[i + delta]
#
#         yield i, uma_porta, outra_porta


def executa_analise_hamming(circuito: Circuito):
    # gera a matriz de distancias (toda zerada)
    matriz = gera_matriz_de_distancias(circuito)
    # logger.debug(f'Matriz Dist.: {matriz}')

    # obtem as portas do circuito
    portas = circuito.portas

    # obtem a quantidade de bits que o circuito utiliza
    qtd_bits = circuito.tamanho_circuito + circuito.bits_extras

    # # percorre as portas, analisando as distancias entre elas
    # for delta in range(1, len(portas)):
    #     for i, uma_porta, outra_porta in percorre_portas(portas, delta):
    #         # monta os vetores associados a cada porta
    #         v1 = monta_vetor(uma_porta, qtd_bits)
    #         v2 = monta_vetor(outra_porta, qtd_bits)
    #
    #         # calcula a distancia entre os vetores
    #         distancia = compara_distancia_entre_vetores(v1, v2)
    #
    #         # preenche a distancia na matriz
    #         matriz[i][i + delta] = distancia

    for i in range(len(portas) - 1):
        uma_porta = portas[i]
        vetor_temp = monta_vetor(uma_porta, qtd_bits)

        for j in range(i + 1, len(portas)):
            outra_porta = portas[j]
            v2 = monta_vetor(outra_porta, qtd_bits)

            # calcula a distancia entre as duas portas
            distancia, vetor_temp = compara_distancia_entre_vetores(vetor_temp, v2)
            # logger.debug(f'd={distancia} :: v={vetor_temp}')

            matriz[i][j] = distancia

    return matriz


def imprime_matriz(m: List[List[int]], inicial=1):
    msg = 'Matriz de distancias:\n'
    msg += ' ' * 5

    for i in range(0, len(m)):
        msg += f'{i + inicial:3d}'
        msg += ' ' * 2

    msg += '\n    '
    msg += '-' * (len(m) * 5)
    msg += '\n'

    for i in range(len(m)):
        s = f'{i + inicial:3d}|'
        for j in range(len(m)):
            s += f' {m[i][j]:3d} '
        msg += f'{s}\n'

    logger.debug(msg)


def separa_subcircuito(subcirc: Circuito):
    ## coleta informacao sobre todos os alvos e controles
    todos_ctrls = set()

    for porta in subcirc:
        ctrls = porta.controles
        todos_ctrls.update(ctrls)
    logger.debug(f'Todos ctrls: {todos_ctrls}')

    ## analisa quais controles sao comuns a todas as portas
    ctrls_comuns = todos_ctrls
    for porta in subcirc:
        ctrls = porta.controles
        s_ctrls = set(ctrls)
        ctrls_comuns = ctrls_comuns.intersection(s_ctrls)
    logger.debug(f'Controles em comum: Controles={ctrls_comuns}')

    ## monta as partes comuns
    controles_comuns = copy.deepcopy(ctrls_comuns)
    # controles_comuns = list()
    # for controle_distinto in ctrls_comuns:
    #     controle = Controle(controle_distinto.linha, controle_distinto.sinal)
    #     controles_comuns.append(controle)
    # logger.debug(f'Partes Comuns: {controles_comuns}')

    portas_diff = list()
    logger.debug(f'Removendo controles em comum...')
    for porta in subcirc:
        # obtem uma cópia da porta
        p = porta.obtem_copia()
        logger.debug(f'Antes Porta: {p}')

        # remove os controles comuns da porta
        p.remove_controles(controles_comuns)
        logger.debug(f'Depois Porta: {p}')

        # adiciona a porta modificada na lista de portas diferentes
        portas_diff.append(p)

    # monta o mapeamento
    mapeamento = dict()

    # busca as linha usadas (nao considerando as partes em comum)
    linhas_usadas = subcirc.obtem_linhas_usadas()
    for ctrl in controles_comuns:
        linhas_usadas = linhas_usadas - {ctrl.linha}
    logger.debug(f'Linhas usadas (sem as partes em comum): {linhas_usadas}')

    if len(linhas_usadas) > 3:
        return None, subcirc

    i = 0
    for x in linhas_usadas:
        mapeamento[x] = i
        i += 1
    logger.debug(f'Mapeamento ==> {mapeamento}')

    # cria o subcircuito com as partes diferentes
    subcirc_diff = Circuito(portas=portas_diff,
                            qtd_vars=subcirc.tamanho_circuito,
                            ancillas=subcirc.bits_extras,
                            mapa=mapeamento)

    # retorna os controles em comum (pra adição posterior na junção) e o subcircuito contendo somente as partes diff
    return controles_comuns, subcirc_diff


def gera_subcircuitos(circuito: Circuito, matriz: List[List[int]]):
    i = 0
    subcircuitos = list()

    while i <= len(matriz) - 1:
        temp = matriz[i]
        logger.info(f'Procurando a partir da porta {i + 1}')
        logger.debug(f'Porta {i + 1} (distancias): {temp}')

        max_pos = encontra_maior_valor_continuo(temp, percorrer_inicio=i + 1)

        if max_pos > i:
            logger.info(f'Intervalo de portas escolhido: {i + 1} ~ {max_pos + 1}')

            subcircuito = Circuito(portas=circuito.portas[i:max_pos + 1],
                                   qtd_vars=circuito.tamanho_circuito,
                                   ancillas=circuito.bits_extras)
            logger.debug(f'Subcircuito:\n{subcircuito}')

            # atualiza o valor de {i} para começar a partir da próxima porta
            i = max_pos + 1
        else:
            logger.info(f'Não existe uma porta que satisfaz')
            subcircuito = Circuito(portas=circuito.portas[i:i + 1],
                                   qtd_vars=circuito.tamanho_circuito,
                                   ancillas=circuito.bits_extras)
            logger.debug(f'Subcircuito:\n{subcircuito}')

            # atualiza o valor de {i} para começar a partir da próxima porta
            i += 1

        parte_em_comum, parte_diferente = separa_subcircuito(subcircuito)
        # logger.debug(f'Parte comum: {type(parte_em_comum)} :: {parte_em_comum}')
        # logger.debug(f'Parte diff: {type(parte_diferente)} :: {parte_diferente}')
        subcircuitos.append([parte_em_comum, parte_diferente])

    return subcircuitos


def encontra_maior_valor_continuo(vetor: List[int], maior_distancia_possivel: int = 3, percorrer_inicio: int = 0):
    maior_indice = 0
    i = percorrer_inicio

    while i < len(vetor) and vetor[i] <= maior_distancia_possivel:
        maior_indice = i
        i += 1

    return maior_indice


def junta_subcircuito(partes_em_comum: set, partes_diferentes: Circuito):
    for porta in partes_diferentes:
        logger.debug(f'Adicionando partes em comum na porta:\nComum: {partes_em_comum}\nPorta: {porta}')
        porta.adiciona_controles(partes_em_comum)

    # atualiza a informacao do circuito, usando as informacoes atualizadas das portas
    logger.debug(f'Atualizando informações da porta...')
    partes_diferentes.atualiza_informacoes()
    logger.debug(f'Informações atualizadas')

    return partes_diferentes


def encontra_subcircuito_otimo(parte_diferente: Circuito, base_permutacoes: dict):
    linhas_usadas = len(parte_diferente.obtem_linhas_usadas())
    permutacao = parte_diferente.obtem_permutacao(qtd_bits=linhas_usadas)
    # logger.debug(f'Permutacao = {permutacao} ----------- {type(permutacao)}')

    # for k, v in base_permutacoes.items():
    #     print(type(k), k)
    #     print(type(v), v)
    #     return

    otimo = base_permutacoes.get(permutacao)
    if otimo is not None:
        otimo = copy.deepcopy(otimo)
    logger.debug(f'Circuito ótimo encontrado:\n{otimo}')

    # if otimo is None:
    #     raise Exception(f'Permutação {permutacao} inválida.')

    return otimo


def remapeia_otimo_pro_original(otimo: Circuito, subcirc: Circuito):
    otimo_map = otimo.mapeamento
    logger.debug(f'Mapeamento do circuito otimo: {otimo_map}')
    subcirc_map = subcirc.mapeamento
    logger.debug(f'Mapeamento do subcircuito gerado: {subcirc_map}')

    novo_mapeamento = dict()
    for k, v in subcirc_map.items():
        novo_mapeamento[v] = k
    logger.debug(f'Mapeamento novo (otimo --> subcirc): {novo_mapeamento}')

    for porta in otimo:
        # print(f'Porta Original: {porta}')
        # print(f'\t\tAlvo: {porta.alvos}')
        # for ctrl in porta.controles:
        #     print(f'\t\tControle: {ctrl}')

        porta.remapeia(novo_mapeamento)

        # print(f'Porta Modificada: {porta}')
        # print(f'\t\tAlvo: {porta.alvos}')
        # for ctrl in porta.controles:
        #     print(f'\t\tControle: {ctrl}')

    linhas_usadas = otimo.obtem_linhas_usadas()
    logger.debug(f'Linhas usadas: {linhas_usadas}')
    maior_linha = 1 + max(linhas_usadas, default=0)
    logger.debug(f'Maior linha: {maior_linha}')
    otimo.tamanho_circuito = maior_linha
    mapa = [(i, i) for i in range(otimo.tamanho_circuito)]
    otimo.mapeamento = dict(mapa)
    logger.debug(f'Otimo novo tam: {otimo.tamanho_circuito}')
    logger.debug(f'Otimo novo map: {otimo.mapeamento}')

    return otimo


def otimiza_com_circuito_minimo(circuito: Circuito, usa_reed_muller=True):
    matriz = executa_analise_hamming(circuito)
    # imprime_matriz(matriz)

    subcircs = gera_subcircuitos(circuito, matriz)
    base_permutacoes = preload_permutacoes()

    subcircs_otimizados = list()
    for i, sub in enumerate(subcircs):
        comum, subcirc = sub
        logger.debug(f'Subcircuito #{i} é formado por:\n(1) Controles em comum: {comum}\n(2) {subcirc}')

        circ = subcirc
        if comum is None:
            logger.debug(f'Não existe controles em comum, o que indica que mais de 3 linhas estão sendo utilizadas.')
            logger.debug(f'Circuito avaliado:\n{subcirc}')

            # if usa_reed_muller:
            #     # caso mais de três estejam sendo utilizadas, usamos a estrategia de reed-muller
            #     circ = executa_pos_sintese(subcirc)
            #     logger.debug(f'Circuito com aplicação do RM:\n{circ}')

        else:
            subcirc_otimo = encontra_subcircuito_otimo(subcirc, base_permutacoes)
            subcirc = remapeia_otimo_pro_original(subcirc_otimo, subcirc)
            logger.debug(f'Circuito remapeado:\n{subcirc}')

            circ = junta_subcircuito(comum, subcirc)
            logger.debug(f'Circuito após junção:\n{circ}')

        # armazena o subcircuito otimizado
        subcircs_otimizados.append(circ)

    circuito_otimizado = Circuito()
    for circ in subcircs_otimizados:
        # logger.debug(f'Map.Circ: {type(circ)} :: {circ.mapeamento}')
        # logger.debug(f'Map.Port: {type(circ.portas)} :: {circ.obtem_mapeamentos()}')
        logger.debug(f'Adicionando subcircuito no circuito final:\n{circ}')
        circuito_otimizado = circuito_otimizado + circ
    logger.debug(f'Circuito Otimizado:\n{circuito_otimizado}')
    logger.debug(f'Mapa Otimizado: {circuito_otimizado.mapeamento}')

    return circuito_otimizado


if __name__ == '__main__':
    circuito = realiza_leitura_tfc('./tfcs/teste/teste07.tfc')
    logger.info(f'Circuito analisado:\n{circuito}')

    otimiza_com_circuito_minimo(circuito, usa_reed_muller=True)
