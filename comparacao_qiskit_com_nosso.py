from novo.benchmark.benchmark_util import consolida_benchmark, realiza_benchmark
from novo.otimizador.comparacao_qiskit.sintese_qiskit import executa_comparacao_qiskit


def executa_comparacao(seed=10, n_inicial=8, n_final=8, qtd_testes_por_n=10, diretorio='./tfcs/sintese_qiskit/'):
    executa_comparacao_qiskit(
        seed=seed,
        n_inicial=n_inicial,
        n_final=n_final,
        qtd_testes_por_n=qtd_testes_por_n,
        diretorio=diretorio
    )


# def verifica_memoria(g=16):
#     circ = realiza_leitura_tfc('./tfcs/teste/teste08_ancillas.tfc')
#     print(f'Circuito Original:\n{circ}')
#
#     p = circ.obtem_permutacao(qtd_bits=g)
#     p2 = np.array(p, dtype='object')
#     s, s2 = getsizeof(p), sys.getsizeof(p2)
#     print(type(p), f'{s:,}', '-->', type(p2), f'{s2:,}', ':::', f'{100*(1-s2/s):2.4f}')
#
#     # t = circ.obtem_tabela_verdade(n=g, ancillas=0)
#     # t2 = np.array(t, dtype=np.uint8)
#     # s, s2 = getsizeof(t), sys.getsizeof(t2)
#     # print(type(t), f'{s:,}', '-->', type(t2), f'{s2:,}', ':::', f'{100 * (1-s2 / s):2.4f}')
#     time.sleep(5)


def compara_qiskit():
    diretorio_tfcs = './tfcs/sintese_qiskit/'
    diretorio_benchmarks = './benchmark/algoritmo_sintese/'
    qtd_threads = 2

    # executa_comparacao(diretorio=diretorio_tfcs)
    realiza_benchmark(diretorio_base=diretorio_tfcs, diretorio_destino=diretorio_benchmarks, qtd_threads=qtd_threads)
    consolida_benchmark(diretorio=diretorio_benchmarks)

    # verifica_memoria(20)
    # circ = realiza_leitura_tfc('./tfcs/sintese_qiskit/n5/n5_s10_t001_linear.tfc')
    # executa_regras(circ)
    # executa_otimos(circ)
    # executa_reed(circ)

    print('End.')


if __name__ == '__main__':
    compara_qiskit()
