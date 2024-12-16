import csv
import json

# https://docs.sympy.org/latest/modules/combinatorics/permutations.html
from sympy.combinatorics import Permutation


def read_json(json_name):
    f = open(json_name, 'r')
    temp_data = json.load(f)

    delimitador = 'T'

    for key, value in temp_data.items():
        clean_value = value.replace('[', '').replace(']', '')
        clean_value = [delimitador + s for s in clean_value.split(delimitador)]
        clean_value = [s.strip(', ') for s in clean_value]
        clean_value = clean_value[1:]

        permutacao_real = eval(key)

        yield permutacao_real, clean_value


def write_csv(filename, content):
    header = ['Array Form', 'Cyclic Form', '#Gates', 'Gates', 'Parity', 'Hermitian']

    with open(filename, 'w') as f:
        w = csv.writer(f)

        w.writerow(header)
        w.writerows(content)


def process_json(json_name):
    info = list()

    for permutation, gates in read_json(json_name):
        perm = [int(p, 2) for p in permutation]
        perm = Permutation(perm)
        #print(dir(perm))

        info_ = [
            perm.array_form, perm.full_cyclic_form,
            len(gates), gates,
            len(gates) % 2 == 0,
            (perm * perm) == Permutation(range(perm.size)),
        ]

        info.append(info_)

    return info


def main():
    info = list()

    info2bits = process_json(f'./data/permutacoes/json/permutacao_2bits.json')
    info.extend(info2bits)

    info3bits = process_json(f'./data/permutacoes/json/permutacao_3bits.json')
    info.extend(info3bits)

    for i in info: print(i)

    write_csv('./data/permutacoes/json/kowada.csv', info)


if __name__ == '__main__':
    main()
