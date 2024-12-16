from novo.circuitos.circuito import Circuito
from novo.logs.logging_utils import create_logger
from novo.otimizador.analisador_matriz_hamming.analisador_hamming import otimiza_com_circuito_minimo
from novo.otimizador.otimizador_util import verifica_otimizacao
from novo.regras import aplica_swap, pode_aplicar_swap, aplica_move, pode_aplicar_move, \
    aplica_eliminacao_de_portas_iguais, aplica_eliminacao_de_not_duplicado, aplica_merge, aplica_swap_no_circuito, \
    aplica_move_no_circuito

logger = create_logger('otimizador_circuitos', level='INFO')


def obtem_linhas(portas_subcircuito, porta):
    """
    funcao temporaria -- precisa remover depois

    @param portas_subcircuito: as portas que compoe o subcircuito
    @param porta: a porta atual que esta sendo analisada
    @return: (considerando a porta atual) as linhas usadas, as linhas de alvo, e as linhas de controle
    """
    subc = Circuito(portas_subcircuito)

    linhas_alvo_subcircuito = subc.obtem_linhas_de_alvo_usadas()
    linhas_alvo_porta = porta.obtem_linhas_de_alvo_usadas()
    linhas_alvo = linhas_alvo_subcircuito.union(linhas_alvo_porta)

    linhas_ctrl_subcircuito = subc.obtem_linhas_de_controle_usadas()
    linhas_ctrl_porta = porta.obtem_linhas_de_controle_usadas()
    linhas_ctrl = linhas_ctrl_subcircuito.union(linhas_ctrl_porta)

    linhas_usadas = linhas_alvo.union(linhas_ctrl)

    return linhas_usadas, linhas_alvo, linhas_ctrl


# def agrupa_circuito_com_mesmo_alvo(c: Circuito):
#     if len(c) <= 1:
#         return c
#
#     subcircuito = list()
#     circuito_final = list()
#
#     portas = c.portas
#     for i in range(len(portas) - 1):
#         porta = portas[i]
#         proxima_porta = portas[i + 1]
#
#         linhas_usadas1, linhas_alvo1, linhas_ctrl1 = obtem_linhas(subcircuito, porta)
#         print(f'Porta atual: {porta} :: Linhas = {linhas_usadas1}, {linhas_alvo1}, {linhas_ctrl1}')
#
#         linhas_usadas2, linhas_alvo2, linhas_ctrl2 = obtem_linhas(subcircuito, proxima_porta)
#         print(f'Porta próx.: {proxima_porta} :: Linhas = {linhas_usadas2}, {linhas_alvo2}, {linhas_ctrl2}')
#
#     circuito_reorganizado = Circuito(circuito_final)
#     return circuito_reorganizado


# def agrupo_circuito_com_alvos_diferentes(c: Circuito):
#     pass


def reorganiza_usando_swaps3(c: Circuito):
    if len(c) < 1:
        return c

    n = c.tamanho_circuito
    a = c.bits_extras

    subcircuito = list()
    circuito_final = list()

    portas = c.portas
    for i in range(len(portas) - 1):
        porta = portas[i]
        proxima_porta = portas[i + 1]

        linhas_usadas1, _, _ = obtem_linhas(subcircuito, porta)
        logger.debug(f'Porta atual: {porta} :: Linhas = {linhas_usadas1}')

        linhas_usadas2, _, _ = obtem_linhas(subcircuito, proxima_porta)
        logger.debug(f'Porta próx.: {proxima_porta} :: Linhas = {linhas_usadas2}')

        linhas_usadas = min(len(linhas_usadas1), len(linhas_usadas2))
        # print(f'Linhas usadas: {linhas_usadas}')
        # print(f'Subcirc: {subcircuito}')

        if linhas_usadas > 3:
            logger.debug('<<< parei de adicionar e criei um novo subcirc')
            circuito_final += subcircuito

            # subcircuito_temp = Circuito(subcircuito)
            # logger.debug(f'\nQTD={len(subcircuito_temp)} :: {linhas_usadas=} :: S=\n{subcircuito_temp}\n')

            # começa um novo subcircuito
            subcircuito = [porta]
            continue

        if len(linhas_usadas2) <= len(linhas_usadas1):
            # tenta fazer um SWAP ou MOVE
            if pode_aplicar_move(porta, proxima_porta):
                logger.debug('\t>>> pode aplicar MOVE')
                porta, proxima_porta = aplica_move(porta, proxima_porta)

                portas[i] = porta
                portas[i + 1] = proxima_porta

                logger.debug('>>> adicionando mais uma porta (usando a próxima com MOVE)')
                subcircuito.append(porta)

            elif pode_aplicar_swap(porta, proxima_porta):
                logger.debug('>>> pode aplicar SWAP')
                porta, proxima_porta = aplica_swap(porta, proxima_porta)

                portas[i] = porta
                portas[i + 1] = proxima_porta

                logger.debug('>>> adicionando mais uma porta (usando a próxima com SWAP)')
                subcircuito.append(porta)

            else:
                if len(linhas_usadas1) > 3:
                    logger.debug('<<< nao é possivel adicionar mais uma porta, criei um novo subcirc')
                    circuito_final += subcircuito

                    # subcircuito_temp = Circuito(subcircuito)
                    # logger.debug(f'\nQTD={len(subcircuito_temp)} :: {linhas_usadas=} :: S=\n{subcircuito_temp}\n')

                    # começa um novo subcircuito
                    subcircuito = [porta]
                    continue
                else:
                    logger.debug('>>> adicionando mais uma porta (usando a atual pois não é possível SWAP/MOVE)')
                    subcircuito.append(porta)

        else:
            logger.debug('>>> adicionando mais uma porta (usando atual)')
            subcircuito.append(porta)

        logger.debug(f'QTD={len(subcircuito)} :: L={linhas_usadas} :: S={subcircuito}')

    logger.debug(f'>>> adicionando a porta restante (Porta: {portas[-1]})')
    subcircuito.append(portas[-1])

    if len(subcircuito) > 0:
        circuito_final += subcircuito

    circuito_reorganizado = Circuito(circuito_final, qtd_vars=n, ancillas=a)
    return circuito_reorganizado


# def reduz_circuito_usando_circuitos_otimos(c: Circuito, arquivo_permutacao_min=1, arquivo_permutacao_max=3):
#     base_permutacoes = dict()
#     circuito_final = Circuito()
#
#     logger.debug('carregando arquivo de permutações...')
#     for qtd_bits in range(arquivo_permutacao_min, arquivo_permutacao_max + 1):
#         perms = carrega_arquivo_permutacao(qtd_bits)
#
#         # for k, v in perms.items():
#         #     logger.debug(f'Permutações {qtd_bits}:: Permutação {k}:\n{v}')
#
#         base_permutacoes.update(perms)
#     logger.debug('carregado!')
#
#     for subcirc in gera_subcircuitos_usando_linhas(c):
#         logger.debug(f'Subcircuito:\n{subcirc}')
#
#         linhas_usadas = subcirc.obtem_linhas_usadas()
#         logger.debug(f'Subcircuito utiliza as linhas: {linhas_usadas}')
#
#         linhas_alvo_usadas = subcirc.obtem_linhas_de_alvo_usadas()
#         logger.debug(f'Subcircuito possui as linhas de alvo: {linhas_alvo_usadas}')
#
#         linhas_ctrl_usadas = subcirc.obtem_linhas_de_controle_usadas()
#         logger.debug(f'Subcircuito possui as linhas de controle: {linhas_ctrl_usadas}')
#
#         tamanho_circuito = subcirc.tamanho_circuito
#         ancillas = subcirc.bits_extras
#         logger.debug(f'Subcircuito possui {tamanho_circuito} variaveis e {ancillas} ancillas')
#
#         # se o subcircuito possui menos de 3 linhas, podemos otimizar usando os circuitos otimos
#         if tamanho_circuito <= arquivo_permutacao_max:
#             permutacao = subcirc.obtem_permutacao()
#             logger.debug(f'Subcircuito possui a permutacao: {permutacao}')
#
#             subcircuito_otimo = base_permutacoes[permutacao]
#             logger.debug(f'Subcircuito otimo referente encontrado:\n{subcircuito_otimo}')
#
#             mapeamento = obtem_mapeamento_do_circuito(subcirc)
#             logger.debug(f'Mapeamento feito: {mapeamento}')
#
#             realiza_mapeamento_do_circuito(mapeamento, subcircuito_otimo)
#             logger.debug(f'Subcircuito otimo mapeado:\n{subcircuito_otimo}')
#
#             # adiciona o subcircuito otimo no circuito final
#             circuito_final = circuito_final + subcircuito_otimo
#             logger.debug(f'Subcircuito otimo adicionado ao circuito final:\n{circuito_final}')
#
#         else:
#             # não existem regras ou circuitos ótimos para n > arquivo_permutacao_max
#             logger.debug(
#                 f'Não podemos otimizar o subcircuito porque não há circuitos otimos para esse caso (n={tamanho_circuito}).\n{subcirc}')
#             circuito_final = circuito_final + subcirc
#
#     return circuito_final
#
#     # for subcirc in monta_subcircuito(c):
#     #     # separa o circuito e guarda os controles iguais
#     #     circ_temp, ctrls_iguais = separa_circuito(subcirc)
#     #
#     #     # ----- faz mapeamento ----
#     #
#     #     # modifica o circ_temp para (re)adicionar os controles iguais
#     #     circ_temp = junta_circuito(circ_temp, ctrls_iguais)
#     #


def reduz_circuito_usando_regras(circ: Circuito):
    aplica_eliminacao_de_portas_iguais(circ)
    logger.debug(f'Circuito após aplicar regra 1 (elim. portas duplicadas):\n{circ}')

    aplica_eliminacao_de_not_duplicado(circ)
    logger.debug(f'Circuito após aplicar regra 2 (elim. NOT duplicados):\n{circ}')

    aplica_merge(circ)
    logger.debug(f'Circuito após aplicar regra 3 (merge):\n{circ}')

    aplica_swap_no_circuito(circ)
    logger.debug(f'Circuito após aplicar regra 4 (swap):\n{circ}')

    aplica_move_no_circuito(circ)
    logger.debug(f'Circuito após aplicar regra 5 (move):\n{circ}')

    return circ


def reduz_circuito_usando_regras_e_circuitos_otimos(circ: Circuito,
                                                    usa_regras: bool = True,
                                                    usa_otimos: bool = True,
                                                    usa_reed: bool = True):
    circ_original = circ.obtem_copia()

    if usa_otimos:
        circ = otimiza_com_circuito_minimo(circ, usa_reed_muller=usa_reed)
        logger.debug(f'Circuito Final usando ótimos:\n{circ}')

    if usa_regras:
        circ = reduz_circuito_usando_regras(circ)
        logger.debug(f'Circuito Final usando regras:\n{circ}')

    logger.debug(f'Circuito Final reduzido:\n{circ}')

    verifica_otimizacao(circ_original, circ)
    return circ


def reorganiza_circuito(circ):
    circ_original = circ.obtem_copia()

    # circ_reorganizado = agrupa_circuito_com_mesmo_alvo(circ)
    # circ_reorganizado = agrupo_circuito_com_alvos_diferentes(circ)

    # organiza usando SWAPs
    circ = reorganiza_usando_swaps3(circ)
    logger.debug(f'Circuito Reorganizado:\n{circ}')

    verifica_otimizacao(circ_original, circ)
    return circ


'''
def otimiza_circuito(nome_tfc):
    # realiza leitura do TFC
    circ = realiza_leitura_tfc(nome_tfc)
    logger.info(f'Circuito Original:\n{circ}')

    # obtem a permutação do circuito, para avaliar se a otimização está correta
    perm_original = circ.obtem_permutacao()
    logger.debug(f'Permutacao Original = {perm_original}')

    # reorganiza o circuito
    circ = reorganiza_circuito(circ, perm_original)

    # aplica as regras e circuitos otimos
    # circ = reduz_circuito_usando_regras_e_circuitos_otimos(circ, perm_original)
    # logger.info(f'Circuito Otimizado Final:\n{circ}')

    ##### TEMP
    # circ.salva_em_arquivo(f'otimizado.tfc')

    for i, sub in enumerate(gera_subcircuitos_usando_linhas(circ)):
        logger.info(f'Subcircuito #{i}:\n{sub}')
'''


if __name__ == '__main__':
    reduz_circuito_usando_regras_e_circuitos_otimos('./tfcs/teste/teste07.tfc')
