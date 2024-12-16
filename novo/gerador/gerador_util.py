import json
import pickle
from datetime import datetime
from itertools import product, permutations
from pathlib import Path

from novo.circuitos.alvo import Alvo
from novo.circuitos.circuito import Circuito
from novo.circuitos.controle import Controle
from novo.circuitos.states import States


def gera_estado_circuitos(qtd_bits):
    estados = dict()

    estados_possiveis = []
    for estado_bit in product('01', repeat=qtd_bits):
        um_estado = ''.join(estado_bit)
        estados_possiveis.append(um_estado)

    for estado_permutacao in permutations(estados_possiveis):
        estados[estado_permutacao] = None

    # define que o estado inicial possui um circuito vazio associado
    estado_inicial = tuple(estados_possiveis)
    circuito_vazio = Circuito([], 0)
    estados[estado_inicial] = circuito_vazio

    return estados


def traduz_porta(p):
    alvos = []
    controles = []
    for linha in range(len(p)):
        if p[linha] == States.alvo:
            alvo = Alvo(linha)
            alvos.append(alvo)

        elif p[linha] == States.ctrl_ausente:
            pass

        elif p[linha] == States.ctrl_positivo:
            controle = Controle(linha, States.ctrl_positivo)
            controles.append(controle)

        elif p[linha] == States.ctrl_negativo:
            controle = Controle(linha, States.ctrl_negativo)
            controles.append(controle)

        else:
            raise Exception(f'Não foi identificado o tipo de P {p[linha]}.')

    return alvos, controles


def salva_circuitos_minimos(circuitos, qtd_bits, nome='circuitos', separa_por_data=False):
    base_dir = f'./data/'

    if separa_por_data:
        d = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_dir = f'./data/{d}'

    Path(base_dir).mkdir(parents=True, exist_ok=True)

    pickle_name = f'{base_dir}/{nome}_{qtd_bits}bits.pickle'

    with open(pickle_name, 'wb') as f:
        pickle.dump(circuitos, f)

    json_name = f'{base_dir}/{nome}_{qtd_bits}bits.json'
    circuitos_str = dict()
    for k, v in circuitos.items():
        chave = str(k)
        valor = v
        if v is not None:
            valor = v.obtem_portas_string()

        circuitos_str[chave] = valor

    with open(json_name, 'w') as f:
        json.dump(circuitos_str, f, indent=4, sort_keys=True)


def carrega_circuitos_minimos(qtd_bits, nome='circuitos'):
    pickle_name = f'./data/{nome}_{qtd_bits}bits.pickle'

    with open(pickle_name, 'rb') as f:
        data = pickle.load(f)

    return data
