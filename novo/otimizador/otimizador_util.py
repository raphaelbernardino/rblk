from typing import List

import numpy as np

from novo.circuitos.alvo import Alvo
from novo.circuitos.circuito import Circuito
from novo.circuitos.controle import Controle
from novo.circuitos.states import States
from novo.circuitos.toffoli import Toffoli
from novo.logs.logging_utils import create_logger
from novo.regras import pode_aplicar_swap, pode_aplicar_move, aplica_swap, aplica_move

logger = create_logger(name='otimizador_util', level='DEBUG')
np.set_printoptions(threshold=np.inf)


# def reorganiza_circuito_agrupando_por_alvo_na_mesma_linha(circ: Circuito):
#     """
#
#
#     @param circ:
#     @return:
#     """
#     circuito_reorganizado = Circuito()
#
#     return circuito_reorganizado


# def gera_subcircuitos_com_alvo_na_mesma_linha(circ: Circuito):
#     """
#
#
#     @param circ: O circuito que deve ser reorganizado
#     @return:
#     """
#     subcircuitos = list()
#
#     return subcircuitos


def verifica_otimizacao(circuito_original, circuito_otimizado, lanca_erro=True):
    qtd_bits = max(circuito_original.tamanho_circuito, circuito_otimizado.tamanho_circuito)
    bits_extras = max(circuito_original.bits_extras, circuito_otimizado.bits_extras)

    tbl_original = circuito_original.obtem_tabela_verdade(n=qtd_bits, ancillas=bits_extras)
    tbl_otimizado = circuito_otimizado.obtem_tabela_verdade(n=qtd_bits, ancillas=bits_extras)

    msg_erro = ''

    # if tbl_original != tbl_otimizado:
    if not np.array_equal(tbl_original, tbl_otimizado):
        msg_erro += f'Otimização incorreta. N={qtd_bits} A={bits_extras}\n'
        msg_erro += f'T1 = {tbl_original}\n'
        msg_erro += f'T2 = {tbl_otimizado}'
        logger.error(f'{msg_erro}')

    if msg_erro != '' and lanca_erro:
        raise Exception(f'{msg_erro}')

    # permutacao_original = circuito_original.gera_permutacao()
    # permutacao_otimizado = circuito_otimizado.gera_permutacao()
    #
    # if permutacao_original != permutacao_otimizado:
    #     logger.error(f'P1 = {tbl_original}')
    #     logger.error(f'P2 = {tbl_otimizado}')
    #     raise Exception('Otimização incorreta.')

    return msg_erro


def gera_f1_xor(f, f_alvo):
    f0 = list()
    f1 = list()

    for i in range(len(f)):
        elemento = f_alvo[i] ^ f[i]

        if f_alvo[i] == 0:
            f0.append(elemento)
        else:
            f1.append(elemento)

    if f1 != f0:
        raise Exception(f'F1_XOR INCORRETA.\nF_ALVO = {f_alvo}\nF1a = {f0}\nF1b = {f1}\n')

    return f1


def junta_subcircuitos(subcircuitos_otimizados):
    circuito_otimizado = Circuito()

    for subcircuito in subcircuitos_otimizados:
        logger.debug(f'Adicionando o subcircuito no circuito final:\n{subcircuito}')
        circuito_otimizado = circuito_otimizado + subcircuito
        # logger.debug(f'Circuito Otimizado Parcial\n{circuito_otimizado}')

    logger.info(f'Circuito Otimizado Final\n{circuito_otimizado}')
    return circuito_otimizado


def extrai_coluna_da_matriz(matriz, posicao):
    return [int(linha[posicao]) for linha in matriz]


def le_arquivo(nome_arq):
    """ Retorna o conteúdo completo do arquivo <nome_arq> """
    # from pathlib import Path
    # p = Path('.').absolute()
    # raise Exception(f'Current: {p}')

    with open(nome_arq, 'r') as f:
        conteudo = f.read().lower().split('\n')
    return conteudo


def extrai_quantidade_de_bits_e_vars(linha):
    temp = linha.split(' ')

    qtd_bits = temp[0][1:]

    vars_porta = ''.join(temp[1:])
    vars_porta = [var.strip() for var in vars_porta.split(',')]

    return int(qtd_bits), vars_porta


def extrai_alvos(qtd_alvos, vars_circuito, vars_porta):
    alvos = []

    for i in range(qtd_alvos, 0, -1):
        var_alvo = vars_porta[-i]
        linha_alvo = vars_circuito.index(var_alvo)
        alvo = Alvo(linha_alvo)
        alvos.append(alvo)

    return alvos


def extrai_controles(vars_circuito, vars_controles):
    controles = []

    for var_ctrl in vars_controles:
        var_ctrl_normalizada = var_ctrl.strip("'")
        linha_ctrl = vars_circuito.index(var_ctrl_normalizada)

        sinal_ctrl = States.ctrl_positivo
        if "'" in var_ctrl:
            sinal_ctrl = States.ctrl_negativo

        controle = Controle(linha_ctrl, sinal_ctrl)
        controles.append(controle)

    return controles


def realiza_leitura_tfc(circuito_tfc):
    conteudo = le_arquivo(circuito_tfc)
    circuito = processa_tfc(conteudo)

    return circuito


def processa_tfc(conteudo):
    if isinstance(conteudo, str):
        conteudo = conteudo.split('\n')

    vars_circuito = list()
    portas_circuito = list()

    for linha in conteudo:
        # safety check
        linha = linha.lower()

        # encontrou o trecho de declaração de vars.
        if linha.startswith('.v'):
            linha_vars = linha[3:]
            vars_circuito += [var.strip() for var in linha_vars.split(',')]

        # encontrou uma fredkin
        if linha.startswith('f'):
            raise Exception('Fredkin não é suportada!')

            # qtd_bits, vars_porta = extrai_quantidade_de_bits_e_vars(linha)
            #
            # # extrai o alvo
            # qtd_alvos = 2
            # alvos = extrai_alvos(qtd_alvos, vars_circuito, vars_porta)
            #
            # # extrai os controles
            # vars_controles = vars_porta[:-qtd_alvos]
            # controles = extrai_controles(vars_circuito, vars_controles)
            #
            # porta = Fredkin(alvos, controles)
            # portas_circuito.append(porta)

        # encontrou uma toffoli
        if linha.startswith('t'):
            qtd_bits, vars_porta = extrai_quantidade_de_bits_e_vars(linha)

            # extrai o alvo
            qtd_alvos = 1
            alvos = extrai_alvos(qtd_alvos, vars_circuito, vars_porta)

            # extrai os controles
            vars_controles = vars_porta[:-qtd_alvos]
            controles = extrai_controles(vars_circuito, vars_controles)

            # print(f'Alvos--> {type(alvos)} {alvos}')
            # print(f'Controles--> {type(controles)} {controles}')
            porta = Toffoli(alvos, controles)
            portas_circuito.append(porta)

    # retorna o circuito criado
    circuito = Circuito(portas_circuito, len(vars_circuito) + 0)

    return circuito


# def realiza_escrita_tfc(circuito, nome_arquivo):
#     conteudo_tfc = str(circuito)
#
#     try:
#         with open(nome_arquivo, 'w') as f:
#             f.write(conteudo_tfc)
#
#     except Exception as e:
#         raise e


def obtem_linhas_diferentes_entre_subcircuito_e_porta(subcirc, porta):
    todas_linhas = set()

    # pega as linhas da porta
    linhas_porta = porta.obtem_linhas_usadas()
    todas_linhas = todas_linhas.union(linhas_porta)

    # pega as linhas do subcircuito
    linhas_comum = linhas_porta
    for sub in subcirc:
        linhas = sub.obtem_linhas_usadas()
        todas_linhas = todas_linhas.union(linhas)
        linhas_comum = linhas_comum.intersection(linhas)

    # descobre quais sao linhas que nao aparecem em todas as portas
    diff = set.symmetric_difference(linhas_comum, todas_linhas)

    return diff


def gera_subcircuitos_usando_linhas(circ: Circuito, qtd_max_linhas=3):
    """
    ToDo. retornar o subcircuito e as linhas que são iguais

    atualmente retorna apenas o subcircuito

    as linhas de controle iguais podem ser ignoradas na aferição da qtd. max de linhas
    """
    portas_subcircuito = list()
    linhas_usadas = set()

    for porta in circ:
        logger.debug(f'Porta atual: {porta}')
        linhas_usadas_porta = porta.obtem_linhas_usadas()
        logger.debug(f'Linhas usadas pela porta: {linhas_usadas_porta}')

        linhas_usadas_temp = linhas_usadas.union(linhas_usadas_porta)
        logger.debug(f'Possivel junção da porta resulta em utilizar as linhas: {linhas_usadas_temp}')

        if len(linhas_usadas_temp) > qtd_max_linhas:
            logger.debug('Não pode adicionar essa porta porque ultrapassa o limite máximo de linhas utilizadas.')

            # gera um novo subcircuito
            subcircuito = Circuito(portas_subcircuito, qtd_vars=circ.tamanho_circuito, ancillas=circ.bits_extras)
            yield subcircuito

            # inicia um novo subcircuito
            portas_subcircuito = list()
            linhas_usadas = set()

        else:
            # adiciona a porta no subcircuito
            portas_subcircuito.append(porta)
            logger.debug(f'>>> adicionando porta {porta} no subcircuito. S={portas_subcircuito}')

            # atualiza as informações de linhas utilizadas
            linhas_usadas = linhas_usadas_temp
            logger.debug(f'>>> atualizando informação sobre linhas usadas: L={linhas_usadas}')

    if len(portas_subcircuito) > 0:
        logger.debug('>>> circuito finalizado.')
        subcircuito = Circuito(portas_subcircuito, qtd_vars=circ.tamanho_circuito, ancillas=circ.bits_extras)
        yield subcircuito


def gera_subcircuitos_usando_alvos3(circuito: Circuito, qtd_alvos):
    def mesmosalvos(porta1, porta2):
        alvos1 = porta1.obtem_linhas_de_alvo_usadas()
        alvos2 = porta2.obtem_linhas_de_alvo_usadas()
        return alvos1 == alvos2

    """
    Reorganiza usando as Regras 4 (SWAP) e 5 (MOVE). Após isso particiona o circuito informado, para gerar os
    subcircuitos.

    @param circuito: Circuito a ser particionado.
    @param qtd_alvos: Quantidade máxima de linhas de alvos permitidos em cada subcircuito.
    @return:
    """
    portas: List[Toffoli] = circuito.portas
    subcircuito = list()
    listaSC = list()

    for i in range(len(portas)):
        # logger.debug(f'{i}:Testando a porta {portas[i]}')
        if subcircuito == []:
            subcircuito = [portas[i]]
        else:
            if mesmosalvos(portas[i], subcircuito[-1]):
                subcircuito.append(portas[i])
            else:
                listaSC.append(subcircuito)
                subcircuito = [portas[i]]

        # se ainda houver 3 portas
        if i < len(portas) - 2:
            if not mesmosalvos(portas[i], portas[i + 1]) and mesmosalvos(portas[i], portas[i + 2]):
                if pode_aplicar_swap(portas[i + 1], portas[i + 2]):
                    logger.debug(f'Aplicando SWAP entre {portas[i + 1]} e {portas[i + 2]}')
                    portas[i + 1], portas[i + 2] = aplica_swap(portas[i + 1], portas[i + 2])

                elif pode_aplicar_move(portas[i + 1], portas[i + 2]):
                    logger.debug(f'Aplicando MOVE entre {portas[i + 1]} e {portas[i + 2]}')
                    portas[i + 1], portas[i + 2] = aplica_move(portas[i + 1], portas[i + 2])

    listaSC.append(subcircuito)
    # return listaSC

    # adicionado apos kowada
    lista_circuitos = list()
    for subcirc in listaSC:
        sub = Circuito(subcirc, qtd_vars=circuito.tamanho_circuito, ancillas=circuito.bits_extras)
        lista_circuitos.append(sub)
    return lista_circuitos


# def gera_subcircuitos_usando_alvos2(circ: Circuito, qtd_alvos: int = 1):
#     """
#     ToDo. EM PROCESSO DE PENSAMENTO
#
#     Reorganiza usando as Regras 4 (SWAP) e 5 (MOVE). Após isso particiona o circuito informado, para gerar os
#     subcircuitos.
#
#     @param circ: Circuito a ser particionado.
#     @param qtd_alvos: Quantidade máxima de linhas de alvos permitidos em cada subcircuito.
#     @return:
#     """
#     if len(circ) <= 1:
#         return circ
#
#     # obtem as portas do circuito de entrada
#     portas = circ.portas
#
#     # inicializa uma lista de portas temporaria
#     subcircuito = list()
#
#     # inicializa a lista de portas que constitui o circuito reorganizado
#     portas_reorganizadas = list()
#
#     for i in range(len(portas) - 1):
#         # obtem a porta atual e a proxima porta
#         porta = portas[i]
#         proxima_porta = portas[i + 1]
#         logger.debug(f'Porta Atual: {porta}')
#         logger.debug(f'Porta Prox: {proxima_porta}')
#
#         # verifica se os alvos estão na mesma linha
#         linhas_alvo_porta = porta.obtem_linhas_de_alvo_usadas()
#         linhas_alvo_prox_porta = proxima_porta.obtem_linhas_de_alvo_usadas()
#         linhas_alvo_usadas = linhas_alvo_porta.union(linhas_alvo_prox_porta)
#
#         if len(linhas_alvo_usadas) <= qtd_alvos:
#             # adiciona a porta atual no subcircuito atual
#             logger.debug(f'Adicionando a porta atual no subcircuito :: Porta={porta}')
#             subcircuito.append(porta)
#             logger.debug(f'Subcircuito após adição da porta: {subcircuito}')
#
#         else:
#             # caso os alvos estejam em linhas diferentes, verifica se a proxima porta pode fazer swap/move
#             ## ToDo. qual a prioridade aqui? quem deve ser feito primeiro?
#             if i + 2 < len(portas):
#                 proxima_proxima_porta = portas[i + 2]
#                 logger.debug(f'Porta Prox Prox: {proxima_proxima_porta}')
#
#                 if pode_aplicar_swap(proxima_porta, proxima_proxima_porta):
#                     logger.debug(f'Aplicando SWAP entre {proxima_porta} e {proxima_proxima_porta}')
#                     proxima_porta, proxima_proxima_porta = aplica_swap(proxima_porta, proxima_proxima_porta)
#
#                     # troca a proxima prox porta pela prox prox porta, e vice-versa
#                     logger.debug(f'SWAP Antes:\nPorta[i+1] = {portas[i+1]}\nPorta[i+2] = {portas[i + 2]}')
#                     portas[i + 1] = proxima_porta
#                     portas[i + 2] = proxima_proxima_porta
#                     logger.debug(f'SWAP Depois:\nPorta[i+1] = {portas[i+1]}\nPorta[i+2] = {portas[i + 2]}')
#
#                     # coloca a proxima proxima porta, que antes era a proxima porta, na lista de portas
#                     logger.debug(f'Colocando a porta {proxima_porta} no subcircuito')
#                     subcircuito.append(proxima_proxima_porta)
#                     logger.debug(f'Subcircuito após adição da porta: {subcircuito}')
#
#             else:
#                 logger.debug(f'Só existem duas portas restantes. Atual={porta} e Prox={proxima_porta}')
#
#                 # verifica, entre as duas, se pode fazer swap/move
#                 if pode_aplicar_swap(porta, proxima_porta):
#                     logger.debug(f'Aplicando MOVE entre {porta} e {proxima_porta}')
#                     porta, proxima_porta = aplica_swap(porta, proxima_porta)
#
#                     # troca a proxima porta pela porta atual, e vice-versa
#                     logger.debug(f'MOVE Antes:\nPorta[i]   = {portas[i]}\nPorta[i+1] = {portas[i + 1]}')
#                     portas[i] = porta
#                     portas[i + 1] = proxima_porta
#                     logger.debug(f'MOVE Depois:\nPorta[i]   = {portas[i]}\nPorta[i+1] = {portas[i + 1]}')
#
#                     # coloca a proxima porta, que agora antes era a porta atual, na lista de portas
#                     logger.debug(f'Colocando a porta {proxima_porta} no subcircuito')
#                     subcircuito.append(proxima_porta)
#                     logger.debug(f'Subcircuito após adição da porta: {subcircuito}')
#
#                 # elif pode_aplicar_move(porta, proxima_porta):
#                 #     logger.debug(f'Aplicando MOVE entre {porta} e {proxima_porta}')
#                 #     porta, proxima_porta = aplica_move(porta, proxima_porta)
#                 #
#                 #     # troca a proxima porta pela porta atual, e vice-versa
#                 #     logger.debug(f'MOVE Antes:\nPorta[i]   = {portas[i]}\nPorta[i+1] = {portas[i + 1]}')
#                 #     portas[i] = porta
#                 #     portas[i + 1] = proxima_porta
#                 #     logger.debug(f'MOVE Depois:\nPorta[i]   = {portas[i]}\nPorta[i+1] = {portas[i + 1]}')
#                 #
#                 #     # coloca a proxima porta, que agora antes era a porta atual, na lista de portas
#                 #     logger.debug(f'Colocando a porta {proxima_porta} no subcircuito')
#                 #     subcircuito.append(proxima_porta)
#                 #     logger.debug(f'Subcircuito após adição da porta: {subcircuito}')
#
#                 else:
#                     # caso nenhuma regra possa ser aplicada, adiciona o subcircuito atual no circuito final
#                     logger.debug('Nenhum regra pode ser aplicada. Reiniciando o subcircuito...')
#                     if len(subcircuito) > 0:
#                         # portas_reorganizadas += subcircuito
#                         portas_reorganizadas.append(subcircuito)
#                         logger.debug(f'Portas reorganizadas = {portas_reorganizadas}')
#
#                     # e gera um novo contendo apenas a porta atual
#                     subcircuito = [porta]
#                     logger.debug(f'Subcircuito = {subcircuito}')
#
#     # adiciona a porta restante na lista de subcircuitos
#     subcircuito.append(portas[-1])
#
#     # e depois esse subcircuito no circuito final
#     # portas_reorganizadas += subcircuito
#     portas_reorganizadas.append(subcircuito)
#
#     # circuito_reorganizado = Circuito(portas_reorganizadas,
#     #                                  qtd_vars=circ.tamanho_circuito,
#     #                                  ancillas=circ.bits_extras)
#     # perm_inicial = circ.obtem_permutacao()
#     # perm_final = circuito_reorganizado.obtem_permutacao()
#     #
#     # if perm_final != perm_inicial:
#     #     raise Exception('Opa!')
#
#     logger.info(f'Portas reorganizadas: {portas_reorganizadas}')
#     return portas_reorganizadas


def gera_subcircuitos_usando_alvos(circuito, qtd_alvos):
    """
    Reorganiza usando as Regras 4 (SWAP) e 5 (MOVE). Após isso particiona o circuito informado, para gerar os
    subcircuitos.

    @param circuito: Circuito a ser particionado.
    @param qtd_alvos: Quantidade máxima de linhas de alvos permitidos em cada subcircuito.
    @return:
    """
    alvos = set()
    subcircuitos = list()
    portas = list()

    qtd_linhas = circuito.tamanho_circuito + circuito.bits_extras

    for porta in circuito:
        alvo = porta.alvos
        logger.debug(f'Porta :: {porta}')
        logger.debug(f'Alvo = {alvo}')

        temp_alvos = set([alvo])
        temp_alvos = temp_alvos.union(alvos)
        logger.debug(f'{temp_alvos=}')

        # se o alvo atual nao afeta a quantidade máxima de alvos, adicione a porta no subcircuito;
        # c.c comece um novo subcircuito;
        if len(temp_alvos) <= qtd_alvos:
            logger.debug(f'Adicionando porta {porta}')

            # adiciona a porta
            portas.append(porta)

            # adiciona o alvo
            alvos.add(alvo)
        else:
            logger.debug('Comecando um novo subcircuito')

            # gera um subcircuito a partir das portas geradas
            subcircuito = Circuito(portas, qtd_linhas)
            logger.debug(f'Subcircuito #{len(subcircuitos)} :: {subcircuito}')

            # salva o subcircuito
            subcircuitos.append(subcircuito)

            # começa outro subcircuito
            portas = [porta]
            alvos = {porta.alvos}

    if len(portas) > 0:
        subcircuito = Circuito(portas, qtd_linhas)
        subcircuitos.append(subcircuito)

    return subcircuitos


def carrega_arquivo_permutacao(qtd_bits, use_pickle=False):
    data = dict()

    if use_pickle:
        import pickle
        pickle_name = f'./data/permutacoes/pickle/permutacao_{qtd_bits}bits.pickle'
        logger.debug(f'Carregando arquivo pickle {pickle_name}')
        with open(pickle_name, 'rb') as f:
            data = pickle.load(f)

    else:
        import json
        json_name = f'./data/permutacoes/json/permutacao_{qtd_bits}bits.json'
        logger.debug(f'Carregando arquivo json {json_name}')
        f = open(json_name, 'r')
        temp_data = json.load(f)

        delimitador = 'T'

        for key, value in temp_data.items():
            clean_value = value.replace('[', '').replace(']', '')
            clean_value = [delimitador + s for s in clean_value.split(delimitador)]
            clean_value = [s.strip(', ') for s in clean_value]
            clean_value = clean_value[1:]

            nome_vars = [f'b{i}' for i in range(qtd_bits)]

            portas = list()
            for v in clean_value:
                porta = interpreta_string_toffoli(v, nome_vars)
                portas.append(porta)

            permutacao_real = eval(key)
            data[permutacao_real] = Circuito(portas, qtd_bits)

    return data


def interpreta_string_toffoli(linha, nome_vars):
    # logger.debug(f'Linha = {linha}')
    # logger.debug(f'Vars = {nome_vars}')

    # separa o tipo da toffoli e os gates
    linha_gate = linha.split(' ')
    toffoli = linha_gate[0]
    gates = linha_gate[1].split(',')

    # quantos controles?
    qtd_controles = int(toffoli[1:]) - 1

    # linha do alvo?
    var_alvo = gates[-1]
    alvo = nome_vars.index(var_alvo)

    # remove o alvo dos gates
    gates = gates[:-1]

    # cria a lista de controles
    controles = list()
    for g in gates:
        # controle/sinal 0 = positivo;
        sinal = States.ctrl_positivo
        var_ctrl = g

        # controle/sinal 1 = negativo
        if "'" in g:
            sinal = States.ctrl_negativo
            var_ctrl = g[:-1]

        # busca a linha de controle
        linha = nome_vars.index(var_ctrl)

        # empacota os dados e adiciona em uma lista
        # logger.debug(f'Linha = {linha}')
        # logger.debug(f'Sinal = {sinal}')
        lc = Controle(linha, sinal)
        controles.append(lc)

    # cria a porta usando o alvo e controles
    alvo = [Alvo(linha=alvo)]
    # logger.debug(f'Alvo ({type(alvo)}) = {alvo}')
    # logger.debug(f'Controles = {controles}')
    porta = Toffoli(alvo, controles)
    # logger.debug(f'Porta = {porta}')

    return porta


def obtem_mapeamento_do_circuito(c: Circuito):
    linhas = sorted(c.obtem_linhas_usadas())
    logger.debug(f'Linhas usadas pelo circuito: {linhas}')

    mapa_linhas = dict()
    for i in range(len(linhas)):
        mapa_linhas[i] = linhas[i]

    return mapa_linhas


def faz_mapeamento(objeto, mapa):
    # logger.debug(f'Objeto {type(objeto)}: {objeto}')
    linha_atual = objeto.linha
    nova_linha = mapa[linha_atual]

    # logger.debug(f'Mapeando linha: {linha_atual} --> {nova_linha}')
    objeto.linha = nova_linha
    # logger.debug(f'Objeto {type(objeto)}: {objeto}')


def realiza_mapeamento_do_circuito(mapa, circuito):
    for porta in circuito:
        alvo = porta.alvos
        faz_mapeamento(alvo, mapa)

        controles = porta.controles
        for ctrl in controles:
            faz_mapeamento(ctrl, mapa)
