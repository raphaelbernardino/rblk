import csv
import os
from pathlib import Path

from novo.otimizador.otimizador_main import executa_regras, executa_otimos, executa_reed


def busca_arquivos(diretorio, extensao):
    if Path(diretorio).is_file():
        yield diretorio

    if not Path(diretorio).exists():
        raise Exception('Directory does not exist!')

    for raiz, subdir, arq in os.walk(diretorio):
        for nome_arq in sorted(arq):
            if nome_arq.endswith(extensao):
                nome_arq_completo = os.path.join(raiz, nome_arq)
                # print(f'{nome_arq_completo}')
                yield nome_arq_completo


def busca_arquivos_tfc(diretorio):
    for arq in busca_arquivos(diretorio=diretorio, extensao='.tfc'):
        yield arq


def realiza_leitura_csv(arquivo):
    if not Path(arquivo).exists():
        raise Exception(f'Arquivo não existe. Verifique o caminho novamente: {arquivo}')

    with open(arquivo, 'r') as f:
        for row in csv.DictReader(f):
            yield row


# def realiza_escrita_csv(arquivo, conteudo, cabecalho=None, modo='a'):
#     # safety-check
#     Path(arquivo).parent.mkdir(parents=True, exist_ok=True)
#
#     with open(arquivo, modo) as f:
#         w = csv.writer(f)
#
#         # escreve cabecalho, se existir
#         if cabecalho is not None:
#             w.writerow(cabecalho)
#
#         # escreve o conteudo
#         w.writerows(conteudo)


def realiza_escrita_csv(arquivo, cabecalho, conteudo, modo='a'):
    # safety-check
    Path(arquivo).parent.mkdir(parents=True, exist_ok=True)

    with open(arquivo, modo) as f:
        w = csv.DictWriter(f, fieldnames=cabecalho)

        w.writeheader()
        w.writerows(conteudo)


def consolida_dicionario(conteudo):
    rows = list()
    header = set()

    for k in conteudo:
        temp = dict()
        temp['Nome TFC'] = k
        temp.update(conteudo[k])

        # row = list(temp.values())
        for h in temp.keys():
            header.add(h)

        # # nao adiciona cabecalho
        # if 'Nome TFC' in row:
        #     continue

        # rows.append(row)
        rows.append(temp)

    header.remove('Nome TFC')
    header = sorted(header)
    header = ['Nome TFC'] + sorted(header, key=len)
    print(f'Header: {header}')

    return header, rows


def realiza_benchmark(diretorio_base, diretorio_destino, qtd_threads=2, salvar_circuitos=True):
    # fix circular import error
    from novo.benchmark.benchmark import Benchmark

    ### BASELINE
    Benchmark(diretorio=f'{diretorio_base}',
              funcao_benchmark=executa_regras,
              nome_arquivo=f'{diretorio_destino}/regras/benchmark_regras.csv',
              salvar_circuitos=salvar_circuitos,
              qtd_threads=qtd_threads,
              )

    Benchmark(diretorio=f'{diretorio_base}',
              funcao_benchmark=executa_otimos,
              nome_arquivo=f'{diretorio_destino}/otimos/benchmark_otimos.csv',
              salvar_circuitos=salvar_circuitos,
              qtd_threads=qtd_threads,
              )

    Benchmark(diretorio=f'{diretorio_base}',
              funcao_benchmark=executa_reed,
              nome_arquivo=f'{diretorio_destino}/reed/benchmark_reed.csv',
              salvar_circuitos=salvar_circuitos,
              qtd_threads=qtd_threads,
              )

    ## REGRAS + ...
    Benchmark(diretorio=f'{diretorio_destino}/regras/',
              funcao_benchmark=executa_otimos,
              nome_arquivo=f'{diretorio_destino}/regras_otimos/benchmark_regras_otimos.csv',
              salvar_circuitos=salvar_circuitos,
              qtd_threads=qtd_threads,
              )

    Benchmark(diretorio=f'{diretorio_destino}/regras/',
              funcao_benchmark=executa_reed,
              nome_arquivo=f'{diretorio_destino}/regras_reed/benchmark_regras_reed.csv',
              salvar_circuitos=salvar_circuitos,
              qtd_threads=qtd_threads,
              )

    ## OTIMOS + ...
    Benchmark(diretorio=f'{diretorio_destino}/otimos/',
              funcao_benchmark=executa_regras,
              nome_arquivo=f'{diretorio_destino}/otimos_regras/benchmark_otimos_regras.csv',
              salvar_circuitos=salvar_circuitos,
              qtd_threads=qtd_threads,
              )

    Benchmark(diretorio=f'{diretorio_destino}/otimos/',
              funcao_benchmark=executa_reed,
              nome_arquivo=f'{diretorio_destino}/otimos_reed/benchmark_otimos_reed.csv',
              salvar_circuitos=salvar_circuitos,
              qtd_threads=qtd_threads,
              )

    ## REED + ...
    Benchmark(diretorio=f'{diretorio_destino}/reed/',
              funcao_benchmark=executa_regras,
              nome_arquivo=f'{diretorio_destino}/reed_regras/benchmark_reed_regras.csv',
              salvar_circuitos=salvar_circuitos,
              qtd_threads=qtd_threads,
              )

    Benchmark(diretorio=f'{diretorio_destino}/reed/',
              funcao_benchmark=executa_otimos,
              nome_arquivo=f'{diretorio_destino}/reed_otimos/benchmark_reed_otimos.csv',
              salvar_circuitos=salvar_circuitos,
              qtd_threads=qtd_threads,
              )

    ### REGRAS + OTIMOS + REED
    Benchmark(diretorio=f'{diretorio_destino}/regras_otimos/',
              funcao_benchmark=executa_reed,
              nome_arquivo=f'{diretorio_destino}/regras_otimos_reed/benchmark_regras_otimos_reed.csv',
              salvar_circuitos=salvar_circuitos,
              qtd_threads=qtd_threads,
              )

    ### REGRAS + REED + OTIMOS
    Benchmark(diretorio=f'{diretorio_destino}/regras_reed/',
              funcao_benchmark=executa_otimos,
              nome_arquivo=f'{diretorio_destino}/regras_reed_otimos/benchmark_regras_reed_otimos.csv',
              salvar_circuitos=salvar_circuitos,
              qtd_threads=qtd_threads,
              )

    ### OTIMOS + REGRAS + REED
    Benchmark(diretorio=f'{diretorio_destino}/otimos_regras/',
              funcao_benchmark=executa_reed,
              nome_arquivo=f'{diretorio_destino}/otimos_regras_reed/benchmark_otimos_regras_reed.csv',
              salvar_circuitos=salvar_circuitos,
              qtd_threads=qtd_threads,
              )

    ### OTIMOS + REED + REGRAS
    Benchmark(diretorio=f'{diretorio_destino}/otimos_reed/',
              funcao_benchmark=executa_regras,
              nome_arquivo=f'{diretorio_destino}/otimos_reed_regras/benchmark_otimos_reed_regras.csv',
              salvar_circuitos=salvar_circuitos,
              qtd_threads=qtd_threads,
              )

    ### REED + REGRAS + OTIMOS
    Benchmark(diretorio=f'{diretorio_destino}/reed_regras/',
              funcao_benchmark=executa_otimos,
              nome_arquivo=f'{diretorio_destino}/reed_regras_otimos/benchmark_reed_regras_otimos.csv',
              salvar_circuitos=salvar_circuitos,
              qtd_threads=qtd_threads,
              )

    ### REED + OTIMOS + REGRAS
    Benchmark(diretorio=f'{diretorio_destino}/reed_otimos/',
              funcao_benchmark=executa_regras,
              nome_arquivo=f'{diretorio_destino}/reed_otimos_regras/benchmark_reed_otimos_regras.csv',
              salvar_circuitos=salvar_circuitos,
              qtd_threads=qtd_threads,
              )


def consolida_benchmark(diretorio, nome_arquivo_consolidado=None, prefixo_arquivos_benchmark='benchmark_'):
    if nome_arquivo_consolidado is None:
        nome_arquivo_consolidado = Path(diretorio, 'consolidado.csv')

    consolidado_info = dict()

    for arquivo in busca_arquivos(diretorio=diretorio, extensao='.csv'):
        if not Path(arquivo).name.startswith(prefixo_arquivos_benchmark):
            print(f'O arquivo {arquivo} não é um benchmark! Pulando processando...')
            continue

        # realiza leitura dos dados de benchmark
        arquivo_csv = realiza_leitura_csv(arquivo)

        for c in arquivo_csv:
            abordagem = Path(arquivo).stem.replace(prefixo_arquivos_benchmark, '')
            # print('Abordagem', abordagem)

            nome_tfc = c['Nome TFC']
            gc_original, qc_original, l_original = c['GC Original'], c['QC Original'], c['L Original']
            gc_otimizado, qc_otimizado, l_otimizado = c['GC Otimizado'], c['QC Otimizado'], c['L Otimizado']
            # observacao = c['Observações']

            inner_dict = {
                # f'GC Original': gc_original,
                # f'QC Original': qc_original,
                # f'L Original': l_original,
                f'GC Otimizado {abordagem}': gc_otimizado,
                f'QC Otimizado {abordagem}': qc_otimizado,
                f'L Otimizado {abordagem}': l_otimizado,
                # f'Observações {abordagem}': observacao,
            }

            # identifica se abordagem é baseline
            if abordagem.count('_') == 0:
                inner_dict['GC Original'] = gc_original
                inner_dict['QC Original'] = qc_original
                inner_dict['L Original'] = l_original

            if nome_tfc not in consolidado_info:
                consolidado_info[nome_tfc] = dict()
            consolidado_info[nome_tfc].update(inner_dict)
            # print('D-->', consolidado_info[nome_tfc])

    # transforma o conteudo de dicionario em listas contendo header e linhas
    header, rows = consolida_dicionario(consolidado_info)
    realiza_escrita_csv(arquivo=nome_arquivo_consolidado, cabecalho=header, conteudo=rows, modo='w')
