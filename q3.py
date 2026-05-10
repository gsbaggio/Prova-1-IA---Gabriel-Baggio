import math
import random

# ============================================================
# FUNÇÕES BASE
# ============================================================

def contar_conflitos(estado):
    """Conta o número de pares de rainhas em conflito."""
    n = len(estado)
    conflitos = 0
    for i in range(n):
        for j in range(i + 1, n):
            # Mesma linha
            if estado[i] == estado[j]:
                conflitos += 1
            # Mesma diagonal
            elif abs(estado[i] - estado[j]) == abs(i - j):
                conflitos += 1
    return conflitos


def obter_vizinhos(estado):
    """
    Gera todos os vizinhos movendo exatamente UMA rainha
    para outra linha da MESMA coluna.
    """
    n = len(estado)
    vizinhos = []
    for coluna in range(n):
        for linha in range(1, n + 1):
            if linha != estado[coluna]:
                vizinho = list(estado)
                vizinho[coluna] = linha
                vizinhos.append(tuple(vizinho))
    return vizinhos


# ============================================================
# HILL-CLIMBING (execução manual detalhada)
# ============================================================

def hill_climbing_detalhado(estado_inicial, max_iteracoes=1000):
    """
    Hill-Climbing com registro detalhado de cada iteração.
    Retorna: histórico de iterações, resultado, tipo de parada.
    """
    atual = tuple(estado_inicial)
    atual_h = contar_conflitos(atual)
    historico = []  # lista de dicts
    motivo_parada = "max_iteracoes"

    for iteracao in range(max_iteracoes):
        vizinhos = obter_vizinhos(atual)
        # Avalia todos os vizinhos
        avaliados = [(n, contar_conflitos(n)) for n in vizinhos]
        # Ordena por h crescente
        avaliados.sort(key=lambda x: x[1])

        best_vizinho, melhor_h = avaliados[0]

        # Registra iteração
        historico.append({
            "iteracao": iteracao,
            "estado": atual,
            "h": atual_h,
            "top5_vizinhos": avaliados[:5],
            "best_vizinho": best_vizinho,
            "melhor_h": melhor_h,
        })

        if atual_h == 0:
            motivo_parada = "solution"
            break

        if melhor_h >= atual_h:
            motivo_parada = "local_max_or_plateau"
            break

        atual = best_vizinho
        atual_h = melhor_h

    # Adiciona estado final
    if motivo_parada == "solution":
        pass  # já registrado
    else:
        # Verifica se foi platô ou máximo local
        if motivo_parada == "local_max_or_plateau":
            vizinhos = obter_vizinhos(atual)
            avaliados = [(n, contar_conflitos(n)) for n in vizinhos]
            avaliados.sort(key=lambda x: x[1])
            melhor_h = avaliados[0][1]
            if melhor_h == atual_h:
                motivo_parada = "plateau"
            else:
                motivo_parada = "local_maximum"

    return historico, atual, atual_h, motivo_parada


# ============================================================
# RANDOM RESTART HILL-CLIMBING
# ============================================================

def hill_climbing_simples(estado, max_iteracoes=1000):
    """Versão simples do HC para uso no Random Restart."""
    atual = tuple(estado)
    atual_h = contar_conflitos(atual)
    passos = 0

    for _ in range(max_iteracoes):
        if atual_h == 0:
            break
        vizinhos = obter_vizinhos(atual)
        avaliados = [(n, contar_conflitos(n)) for n in vizinhos]
        avaliados.sort(key=lambda x: x[1])
        best_vizinho, melhor_h = avaliados[0]
        if melhor_h >= atual_h:
            break
        atual = best_vizinho
        atual_h = melhor_h
        passos += 1

    return atual, atual_h, passos


def hill_climbing_reinicio_aleatorio(num_reinicios=20, n=8, semente=42):
    """Executa HC com reinício aleatório."""
    random.seed(semente)
    resultados = []

    for execucao in range(1, num_reinicios + 1):
        inicial = tuple(random.randint(1, n) for _ in range(n))
        final_estado, h_final, passos = hill_climbing_simples(inicial)
        encontrado = (h_final == 0)
        resultados.append({
            "execucao": execucao,
            "inicial": inicial,
            "passos": passos,
            "h_final": h_final,
            "encontrado": encontrado,
        })

    return resultados


# ============================================================
# SIMULATED ANNEALING
# ============================================================

def recozimento_simulado(estado_inicial, T0=100.0, alpha=0.95, max_iteracoes=10000, semente=42):
    """
    Simulated Annealing para N-Rainhas.
    T0: temperatura inicial
    alpha: fator de resfriamento (T = alpha * T)
    """
    random.seed(semente)
    atual = tuple(estado_inicial)
    atual_h = contar_conflitos(atual)
    T = T0
    passos = 0
    piores_aceitos = []  # exemplos de movimentos piores aceitos

    for i in range(max_iteracoes):
        if atual_h == 0:
            break
        if T < 1e-10:
            break

        # Escolhe vizinho aleatório
        n = len(atual)
        coluna = random.randint(0, n - 1)
        linha = random.randint(1, n)
        while linha == atual[coluna]:
            linha = random.randint(1, n)

        vizinho = list(atual)
        vizinho[coluna] = linha
        vizinho = tuple(vizinho)
        vizinho_h = contar_conflitos(vizinho)

        delta_E = vizinho_h - atual_h  # aumento de conflitos

        if delta_E < 0:
            # Melhora: aceita sempre
            atual = vizinho
            atual_h = vizinho_h
        else:
            # Piora ou igual: aceita com probabilidade e^(-deltaE/T)
            P = math.exp(-delta_E / T)
            if random.random() < P:
                if len(piores_aceitos) < 5:
                    piores_aceitos.append({
                        "passo": i,
                        "de_h": atual_h,
                        "para_h": vizinho_h,
                        "delta_E": delta_E,
                        "T": round(T, 4),
                        "P": round(P, 4),
                    })
                atual = vizinho
                atual_h = vizinho_h

        # Resfriamento
        T = alpha * T
        passos += 1

    return atual, atual_h, passos, piores_aceitos


def executar_rs_multiplas(num_execucoes=20, n=8, T0=100.0, alpha=0.95, max_iteracoes=10000):
    """Executa SA múltiplas vezes para comparação."""
    resultados = []
    for execucao in range(num_execucoes):
        inicial = tuple(random.randint(1, n) for _ in range(n))
        final_estado, h_final, passos, _ = recozimento_simulado(
            inicial, T0=T0, alpha=alpha, max_iteracoes=max_iteracoes, semente=execucao
        )
        resultados.append({
            "run": execucao + 1,
            "h_final": h_final,
            "encontrado": (h_final == 0),
            "passos": passos,
        })
    return resultados


# ============================================================
# IMPRESSÃO DOS RESULTADOS
# ============================================================

def imprimir_separador(caractere="=", largura=80):
    print(caractere * largura)


def imprimir_hill_climbing_manual():
    imprimir_separador()
    print("HILL-CLIMBING MANUAL A PARTIR DE [1,1,1,1,1,1,1,1]")
    imprimir_separador()

    inicial = [1, 1, 1, 1, 1, 1, 1, 1]
    historico, final_estado, h_final, motivo_parada = hill_climbing_detalhado(inicial)

    print(f"\nEstado inicial: {list(inicial)}, h = {contar_conflitos(inicial)}\n")

    # Tabela resumo
    print("TABELA RESUMO DE ITERAÇÕES")
    print(f"{'Iteração':<10} {'Estado':<35} {'h(s)':<6}")
    print("-" * 55)
    for entrada in historico:
        print(f"{entrada['iteracao']:<10} {str(list(entrada['estado'])):<35} {entrada['h']:<6}")

    # Detalhe de cada iteração
    print("\n\nDETALHE DE CADA ITERAÇÃO (Top 5 vizinhos)")
    imprimir_separador("-")
    for entrada in historico:
        it = entrada["iteracao"]
        print(f"\n--- Iteração {it} ---")
        print(f"  Estado atual: {list(entrada['estado'])}, h = {entrada['h']}")
        print(f"  Top 5 vizinhos:")
        print(f"  {'Vizinho':<40} {'h':<5}")
        for viz, viz_h in entrada["top5_vizinhos"]:
            marcador = " <-- ESCOLHIDO" if viz == entrada["best_vizinho"] else ""
            print(f"  {str(list(viz)):<40} {viz_h:<5}{marcador}")
        print(f"  Escolhido: {list(entrada['best_vizinho'])}, h = {entrada['melhor_h']}")
        if entrada['melhor_h'] < entrada['h']:
            print(f"  Motivo: melhor vizinho com h = {entrada['melhor_h']} < {entrada['h']} (melhora)")
        elif entrada['melhor_h'] == entrada['h']:
            print(f"  Motivo: platô (melhor vizinho tem h igual ao atual)")
        else:
            print(f"  Motivo: máximo local (todos vizinhos têm h >= {entrada['h']})")

    print(f"\n\nRESULTADO FINAL")
    imprimir_separador("-")
    print(f"  Estado final: {list(final_estado)}, h = {h_final}")
    print(f"  Total de iterações: {len(historico)}")
    print(f"  Motivo de parada: {motivo_parada}")

    if motivo_parada == "local_maximum":
        print("\n  *** MÁXIMO LOCAL DETECTADO ***")
        print("  Nenhum vizinho tem h menor que o estado atual.")
        print("  A busca ficou presa; não é solução global.")
    elif motivo_parada == "plateau":
        print("\n  *** PLATÔ DETECTADO ***")
        print("  Os melhores vizinhos têm h igual ao estado atual.")
    elif motivo_parada == "solution":
        print("\n  *** SOLUÇÃO GLOBAL ENCONTRADA (h = 0) ***")


def imprimir_reinicio_aleatorio():
    imprimir_separador()
    print("RANDOM RESTART HILL-CLIMBING (20 execuções)")
    imprimir_separador()

    resultados = hill_climbing_reinicio_aleatorio(num_reinicios=20)

    print(f"\n{'Execução':<10} {'Estado inicial':<38} {'Passos':<8} {'h(s) final':<12} {'Solução?'}")
    print("-" * 80)
    solucoes = 0
    for r in resultados:
        encontrado_str = "SIM" if r["encontrado"] else "NÃO"
        if r["encontrado"]:
            solucoes += 1
        print(f"{r['execucao']:<10} {str(list(r['inicial'])):<38} {r['passos']:<8} {r['h_final']:<12} {encontrado_str}")

    print(f"\nTotal de soluções encontradas: {solucoes}/{len(resultados)}")
    avg_passos = sum(r["passos"] for r in resultados) / len(resultados)
    print(f"Média de passos: {avg_passos:.1f}")


def print_recozimento_simulado():
    imprimir_separador()
    print("SIMULATED ANNEALING")
    imprimir_separador()

    T0 = 100.0
    alpha = 0.95
    max_iteracoes = 10000
    inicial = [1, 1, 1, 1, 1, 1, 1, 1]

    final_estado, h_final, passos, piores_aceitos = recozimento_simulado(
        inicial, T0=T0, alpha=alpha, max_iteracoes=max_iteracoes
    )

    print(f"\nParâmetros:")
    print(f"  Temperatura inicial (T0): {T0}")
    print(f"  Fator de resfriamento (alpha): {alpha}")
    print(f"  Política: T_nova = {alpha} * T_atual (resfriamento geométrico)")
    print(f"  Máximo de iterações: {max_iteracoes}")

    print(f"\nResultado (partindo de {list(inicial)}):")
    print(f"  Estado final: {list(final_estado)}, h = {h_final}")
    print(f"  Passos realizados: {passos}")

    print(f"\nExemplos de movimentos piores aceitos:")
    print(f"{'Passo':<8} {'h_antes':<9} {'h_depois':<10} {'delta_E':<6} {'T':<10} {'P(aceitar)'}")
    print("-" * 55)
    for pa in piores_aceitos:
        print(f"{pa['passo']:<8} {pa['de_h']:<9} {pa['para_h']:<10} {pa['delta_E']:<6} {pa['T']:<10} {pa['P']}")

    # Múltiplas execuções para contar soluções
    print(f"\nComparação (20 execuções com estados iniciais aleatórios):")
    sa_resultados = executar_rs_multiplas(num_execucoes=20, T0=T0, alpha=alpha, max_iteracoes=max_iteracoes)
    rr_resultados = hill_climbing_reinicio_aleatorio(num_reinicios=20)

    sa_solucoes = sum(1 for r in sa_resultados if r["encontrado"])
    rr_solucoes = sum(1 for r in rr_resultados if r["encontrado"])
    sa_avg_passos = sum(r["passos"] for r in sa_resultados) / len(sa_resultados)
    rr_avg_passos = sum(r["passos"] for r in rr_resultados) / len(rr_resultados)

    print(f"\n  {'Algoritmo':<30} {'Soluções':<12} {'Média passos'}")
    print(f"  {'-'*55}")
    print(f"  {'Hill-Climbing (RR)':<30} {rr_solucoes}/20      {rr_avg_passos:.1f}")
    print(f"  {'Simulated Annealing':<30} {sa_solucoes}/20      {sa_avg_passos:.1f}")

    print(f"\nQuantidade de soluções válidas (SA, 20 exec.): {sa_solucoes}")


def imprimir_comparacao():
    imprimir_separador()
    print("COMPARAÇÃO DOS ALGORITMOS")
    imprimir_separador()

    # Coleta dados
    rr_resultados = hill_climbing_reinicio_aleatorio(num_reinicios=20)
    sa_resultados = executar_rs_multiplas(num_execucoes=20)

    ra_sols = sum(1 for r in rr_resultados if r["encontrado"])
    rs_sols = sum(1 for r in sa_resultados if r["encontrado"])
    ra_media_h = sum(r["h_final"] for r in rr_resultados) / len(rr_resultados)
    rs_media_h = sum(r["h_final"] for r in sa_resultados) / len(sa_resultados)

    print(f"\n{'Critério':<35} {'Hill-Climbing (RR)':<22} {'Simulated Annealing'}")
    print("-" * 80)
    print(f"{'Qualidade (soluções/20)':<35} {ra_sols:<22} {rs_sols}")
    print(f"{'h médio final':<35} {ra_media_h:<22.2f} {rs_media_h:.2f}")
    print(f"{'Escapa máximos locais':<35} {'Não (reinício)':<22} {'Sim (prob.)'}")
    print(f"{'Sensível ao estado inicial':<35} {'Muito':<22} {'Moderado'}")
    print(f"{'Estabilidade':<35} {'Moderada':<22} {'Variável (T)'}")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    imprimir_hill_climbing_manual()
    print("\n\n")
    imprimir_reinicio_aleatorio()
    print("\n\n")
    print_recozimento_simulado()
    print("\n\n")
    imprimir_comparacao()