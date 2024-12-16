import csv
from pathlib import Path


def escreve_csv_sintese(nome_arquivo: str, informacoes: list, limpa_conteudo_apos_salvar=True):
    try:
        destino = Path(nome_arquivo)
        destino.parent.mkdir(parents=True, exist_ok=True)

        cabecalho = None
        if not destino.exists():
            cabecalho = obtem_cabecalho_sintese()

        with open(destino, 'a') as f:
            w = csv.writer(f)

            if cabecalho:
                w.writerow(cabecalho)
            w.writerow(informacoes)

        if limpa_conteudo_apos_salvar:
            informacoes.clear()

    except Exception as e:
        raise e


def obtem_cabecalho_sintese():
    cabecalho = ['Permutacao',

                 'Sin Unitario GC',
                 'Sin Unitario QC',
                 'Pos Unitario GC',
                 'Pos Unitario QC',

                 'Sin Linear GC',
                 'Sin Linear QC',
                 'Pos Linear GC',
                 'Pos Linear QC',

                 'Sin Permutacao GC',
                 'Sin Permutacao QC',
                 'Pos Permutacao GC',
                 'Pos Permutacao QC',

                 'Sin RM GC',
                 'Sin RM QC',
                 'Pos RM GC',
                 'Pos RM QC',
                 ]
    return cabecalho


def extrai_informacoes_sintese(permutacao, circuitos_sintese, circuitos_pos):
    # valida se todas as abordagens existem
    abordagens_desejadas = {'unitario', 'linear', 'permutacao', 'reed'}
    abordagens_dicionario = set(circuitos_sintese.keys())
    abordagens_faltantes = abordagens_dicionario - abordagens_desejadas
    if len(abordagens_faltantes) > 0:
        raise Exception(f'Verifique as abordagens utilizadas. Faltam as abordagens de sintese: {abordagens_faltantes}')

    # insere a permutacao
    info = [tuple(permutacao)]

    # insere os circuitos unitarios
    info += [circuitos_sintese['unitario'].gc, circuitos_sintese['unitario'].qc]
    info += [circuitos_pos['unitario'].gc, circuitos_pos['unitario'].qc]

    # insere os circuitos linear
    info += [circuitos_sintese['linear'].gc, circuitos_sintese['linear'].qc]
    info += [circuitos_pos['linear'].gc, circuitos_pos['linear'].qc]

    # insere os circuitos permutacao
    info += [circuitos_sintese['permutacao'].gc, circuitos_sintese['permutacao'].qc]
    info += [circuitos_pos['permutacao'].gc, circuitos_pos['permutacao'].qc]

    # insere os circuitos reed
    info += [circuitos_sintese['reed'].gc, circuitos_sintese['reed'].qc]
    info += [circuitos_pos['reed'].gc, circuitos_pos['reed'].qc]

    return info

