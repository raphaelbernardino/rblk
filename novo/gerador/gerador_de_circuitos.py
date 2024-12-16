from itertools import product, permutations

from novo.circuitos.circuito import Circuito
from novo.circuitos.fredkin import Fredkin
from novo.circuitos.states import States
from novo.circuitos.toffoli import Toffoli
from novo.gerador.gerador_util import gera_estado_circuitos, traduz_porta, salva_circuitos_minimos
from novo.logs.logging_utils import create_logger

logger = create_logger('gerador_circuitos_otimos', level='DEBUG')


# =========== FREDKIN =========== =========== FREDKIN =========== =========== FREDKIN ===========
def gera_portas_fredkin(qtd_bits):
    # prepara os estados Fredkin com dois alvos e (n-2) controles, onde n é a qtd. de bits
    estados_fredkin = [States.alvo, States.alvo]
    qtd_controles = qtd_bits - 2

    if qtd_controles < 0:
        return None

    for _ in range(qtd_controles):
        estados_fredkin.append(States.ctrl_ausente)
        estados_fredkin.append(States.ctrl_positivo)
        estados_fredkin.append(States.ctrl_negativo)

    # gera as possibilidades de portas
    for p in permutations(estados_fredkin, r=qtd_bits):
        if p.count(States.alvo) != 2:
            # se não tem os dois alvos, então desconsidera
            continue

        alvos, controles = traduz_porta(p)
        # print(f'p? {p}, alvos? {alvos}, ctrls? {controles}')
        porta = Fredkin(alvos, controles)

        yield porta


def define_portas_fredkin(qtd_bits):
    # define as portas que serão utilizadas
    print(f'===== Portas Fredkin de {qtd_bits} bits')
    portas = []
    for porta in gera_portas_fredkin(qtd_bits):
        # imprime as portas que serão utilizadas
        if porta not in portas:
            print(f'{porta}')
            portas.append(porta)
        # else:
        #     print(f'!!!!! {porta}')

    return portas


def gera_circuitos_minimos_fredkin(qtd_bits, nome='fredkin'):
    portas = define_portas_fredkin(qtd_bits)
    circs = gera_circuitos_minimos(qtd_bits, portas, nome)
    return circs


# =========== TOFFOLI =========== =========== TOFFOLI =========== =========== TOFFOLI ===========
def gera_portas_toffoli(qtd_bits):
    # prepara os estados Toffoli com um alvo e (n-1) controles, onde n é a qtd. de bits
    estados_toffoli = [States.alvo]
    qtd_controles = qtd_bits - 1

    for _ in range(qtd_controles):
        estados_toffoli.append(States.ctrl_ausente)
        estados_toffoli.append(States.ctrl_positivo)
        estados_toffoli.append(States.ctrl_negativo)

    # gera as possibilidades de portas
    for p in permutations(estados_toffoli, r=qtd_bits):
        if p.count(States.alvo) != 1:
            # se não tem um alvo, então desconsidera
            continue

        alvos, controles = traduz_porta(p)
        # print(f'p? {p}, alvos? {alvos}, ctrls? {controles}')
        porta = Toffoli(alvos, controles)

        yield porta


def define_portas_toffoli(qtd_bits):
    # define as portas que serão utilizadas
    # print(f'===== Portas Toffoli de {qtd_bits} bits')
    portas = []
    for porta in gera_portas_toffoli(qtd_bits):
        # imprime as portas que serão utilizadas
        if porta not in portas:
            # print(f'{porta}')
            portas.append(porta)
        # else:
        #     print(f'!!!!! {porta}')

    return portas


def gera_circuitos_minimos_toffoli(qtd_bits, nome='toffoli'):
    portas = define_portas_toffoli(qtd_bits)
    circs = gera_circuitos_minimos(qtd_bits, portas, nome)
    return circs


# =========== TOFFOLI + FREDKIN =========== =========== TOFFOLI + FREDKIN =========== ===========
def gera_circuitos_minimos_toffoli_fredkin(qtd_bits, nome='toffoli_fredkin'):
    portas_toffoli = define_portas_toffoli(qtd_bits)
    portas_fredkin = define_portas_fredkin(qtd_bits)
    portas = portas_toffoli + portas_fredkin
    circs = gera_circuitos_minimos(qtd_bits, portas, nome)
    return circs


# =========== /////// =========== =========== /////// =========== =========== /////// ===========
def escolhe_melhor_circuito(circ1, circ2):
    tam_circ1 = len(circ1)
    tam_circ2 = len(circ2)

    # logger.debug(f'Comparando {circ1} com {circ2}')
    melhor_circ = circ1
    if tam_circ2 < tam_circ1:
        melhor_circ = circ2
    # logger.debug(f'Ganhador {melhor_circ}')

    return melhor_circ


def gera_circuitos_minimos(qtd_bits, portas, nome='circuitos', checkpoint=10000000):
    # chave: permutacao, valor: circuito minimo
    circuitos_minimos = gera_estado_circuitos(qtd_bits)
    print(f'===== Quantidade de circuitos minimos a serem gerados: {len(circuitos_minimos):,}')

    # imprime as combinações de portas possiveis
    print(f'===== Permutações possíveis usando {qtd_bits} bits -- combinando {len(portas)} porta(s)')
    qtd_casos_restantes = len(circuitos_minimos) - 1
    qtd_portas = 1
    while qtd_casos_restantes > 0:
        for i, circ in enumerate(product(portas, repeat=qtd_portas)):
            if (i + 1) % checkpoint == 0:
                print('Salvando checkpoint...')
                salva_circuitos_minimos(circuitos_minimos, qtd_bits, nome)
                print('Salvo!')
                print(f'{i:,} -- {qtd_casos_restantes:,}')

            # gera um circuito
            circ_temp = Circuito(circ, qtd_bits)
            # print(circ_temp)

            # extrai a permutacao a partir do circuito
            permutacao = circ_temp.obtem_permutacao()
            print(f'{i:,} -- {qtd_casos_restantes:,}')
            # print('permutacao', permutacao)

            # mantem somente o menor circuito que gera a permutacao
            permutacao = tuple(permutacao)
            melhor_circ = circuitos_minimos[permutacao]
            if melhor_circ is not None:
                circuitos_minimos[permutacao] = escolhe_melhor_circuito(melhor_circ, circ_temp)
            else:
                qtd_casos_restantes -= 1
                circuitos_minimos[permutacao] = circ_temp
                print(f'{i:,} -- {qtd_casos_restantes:,}')

            # como estamos analisando a qtde de portas, podemos parar no 1o circuito da permutação P
            if qtd_casos_restantes == 0:
                break

        # informa a qtd de portas geradas até o momento
        print(f'Todas as permutações de {qtd_portas} porta(s) foram geradas! Casos restantes: {qtd_casos_restantes:,}')

        # quando todas as possibilidades com {qtd_portas} portas forem geradas, adicione mais uma porta
        qtd_portas += 1

        # salva os circuitos obtidos até agora
        salva_circuitos_minimos(circuitos_minimos, qtd_bits, nome)

    return circuitos_minimos


def executa_gerador_de_circuitos():
    for i in range(0, 3):
        gera_circuitos_minimos_toffoli(qtd_bits=i + 1)


if __name__ == '__main__':
    executa_gerador_de_circuitos()
