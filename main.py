from novo.benchmark.benchmark_util import consolida_benchmark, realiza_benchmark
from novo.logs.logging_utils import create_logger

logger = create_logger('main', level='DEBUG')


# def gera_circuitos_minimos(qtd_bits=2):
#     # circs_min = gera_circuitos_minimos_fredkin(qtd_bits, nome='fredkin')
#     # circuitos = carrega_circuitos_minimos(qtd_bits, nome='fredkin')
#     # print('Salvo corretamente?', circuitos == circs_min)
#
#     # circs_min = gera_circuitos_minimos_toffoli(qtd_bits, nome='toffoli')
#     # circuitos = carrega_circuitos_minimos(qtd_bits, nome='toffoli')
#     # print('Salvo corretamente?', circuitos == circs_min)
#
#     circs_min = gera_circuitos_minimos_toffoli_fredkin(qtd_bits, nome='toffoli_fredkin')
#     circuitos = carrega_circuitos_minimos(qtd_bits, nome='toffoli_fredkin')
#     print('Salvo corretamente?', circuitos == circs_min)


def main():
    # gera_circuitos_minimos(qtd_bits=1)
    # gera_circuitos_minimos(qtd_bits=2)
    # gera_circuitos_minimos(qtd_bits=3)

    # nome_arquivo = './tfcs/edinelco/s2/S2-hwb6.tfc'
    # nome_arquivo = './tfcs/revlib/n_01-09/portas_0-1000/4_49-12-32.tfc'
    # nome_arquivo = './tfcs/teste/teste00.tfc'
    # nome_arquivo = './tfcs/teste/teste02.tfc'
    # nome_arquivo = './tfcs/teste/teste07.tfc'
    # nome_arquivo = './tfcs/edinelco/s2/S2-ex1Miller.tfc'
    # nome_arquivo = './tfcs/edinelco/s2/S2-hwb7_15_inv.tfc'
    # nome_arquivo = './benchmark_aleatorio_otimos_regras_BUH/n3_p10/circuito_aleatorio_0007.tfc'
    # circ = executa_algoritmo_novo(nome_arquivo)

    diretorio_tfcs = './tfcs/pos_sintese/'
    diretorio_benchmarks = './benchmark/algoritmo_novo/'
    qtd_threads = 1
    realiza_benchmark(diretorio_base=diretorio_tfcs, diretorio_destino=diretorio_benchmarks, qtd_threads=qtd_threads)
    consolida_benchmark(diretorio=diretorio_benchmarks)


if __name__ == '__main__':
    main()
