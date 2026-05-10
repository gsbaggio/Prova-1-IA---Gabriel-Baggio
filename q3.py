import math
import random

# ============================================================
# FUNÇÕES BASE
# ============================================================

def count_conflicts(state):
    """Conta o número de pares de rainhas em conflito."""
    n = len(state)
    conflicts = 0
    for i in range(n):
        for j in range(i + 1, n):
            # Mesma linha
            if state[i] == state[j]:
                conflicts += 1
            # Mesma diagonal
            elif abs(state[i] - state[j]) == abs(i - j):
                conflicts += 1
    return conflicts


def get_neighbors(state):
    """
    Gera todos os vizinhos movendo exatamente UMA rainha
    para outra linha da MESMA coluna.
    """
    n = len(state)
    neighbors = []
    for col in range(n):
        for row in range(1, n + 1):
            if row != state[col]:
                neighbor = list(state)
                neighbor[col] = row
                neighbors.append(tuple(neighbor))
    return neighbors


# ============================================================
# HILL-CLIMBING (execução manual detalhada)
# ============================================================

def hill_climbing_detailed(initial_state, max_iter=1000):
    """
    Hill-Climbing com registro detalhado de cada iteração.
    Retorna: histórico de iterações, resultado, tipo de parada.
    """
    current = tuple(initial_state)
    current_h = count_conflicts(current)
    history = []  # lista de dicts
    stop_reason = "max_iter"

    for iteration in range(max_iter):
        neighbors = get_neighbors(current)
        # Avalia todos os vizinhos
        evaluated = [(n, count_conflicts(n)) for n in neighbors]
        # Ordena por h crescente
        evaluated.sort(key=lambda x: x[1])

        best_neighbor, best_h = evaluated[0]

        # Registra iteração
        history.append({
            "iteration": iteration,
            "state": current,
            "h": current_h,
            "top5_neighbors": evaluated[:5],
            "best_neighbor": best_neighbor,
            "best_h": best_h,
        })

        if current_h == 0:
            stop_reason = "solution"
            break

        if best_h >= current_h:
            stop_reason = "local_max_or_plateau"
            break

        current = best_neighbor
        current_h = best_h

    # Adiciona estado final
    if stop_reason == "solution":
        pass  # já registrado
    else:
        # Verifica se foi platô ou máximo local
        if stop_reason == "local_max_or_plateau":
            neighbors = get_neighbors(current)
            evaluated = [(n, count_conflicts(n)) for n in neighbors]
            evaluated.sort(key=lambda x: x[1])
            best_h = evaluated[0][1]
            if best_h == current_h:
                stop_reason = "plateau"
            else:
                stop_reason = "local_maximum"

    return history, current, current_h, stop_reason


# ============================================================
# RANDOM RESTART HILL-CLIMBING
# ============================================================

def hill_climbing_simple(state, max_iter=1000):
    """Versão simples do HC para uso no Random Restart."""
    current = tuple(state)
    current_h = count_conflicts(current)
    steps = 0

    for _ in range(max_iter):
        if current_h == 0:
            break
        neighbors = get_neighbors(current)
        evaluated = [(n, count_conflicts(n)) for n in neighbors]
        evaluated.sort(key=lambda x: x[1])
        best_neighbor, best_h = evaluated[0]
        if best_h >= current_h:
            break
        current = best_neighbor
        current_h = best_h
        steps += 1

    return current, current_h, steps


def random_restart_hill_climbing(num_restarts=20, n=8, seed=42):
    """Executa HC com reinício aleatório."""
    random.seed(seed)
    results = []

    for run in range(1, num_restarts + 1):
        initial = tuple(random.randint(1, n) for _ in range(n))
        final_state, final_h, steps = hill_climbing_simple(initial)
        found = (final_h == 0)
        results.append({
            "run": run,
            "initial": initial,
            "steps": steps,
            "final_h": final_h,
            "found": found,
        })

    return results


# ============================================================
# SIMULATED ANNEALING
# ============================================================

def simulated_annealing(initial_state, T0=100.0, alpha=0.95, max_iter=10000, seed=42):
    """
    Simulated Annealing para N-Rainhas.
    T0: temperatura inicial
    alpha: fator de resfriamento (T = alpha * T)
    """
    random.seed(seed)
    current = tuple(initial_state)
    current_h = count_conflicts(current)
    T = T0
    steps = 0
    worse_accepted = []  # exemplos de movimentos piores aceitos

    for i in range(max_iter):
        if current_h == 0:
            break
        if T < 1e-10:
            break

        # Escolhe vizinho aleatório
        n = len(current)
        col = random.randint(0, n - 1)
        row = random.randint(1, n)
        while row == current[col]:
            row = random.randint(1, n)

        neighbor = list(current)
        neighbor[col] = row
        neighbor = tuple(neighbor)
        neighbor_h = count_conflicts(neighbor)

        delta_E = neighbor_h - current_h  # aumento de conflitos

        if delta_E < 0:
            # Melhora: aceita sempre
            current = neighbor
            current_h = neighbor_h
        else:
            # Piora ou igual: aceita com probabilidade e^(-deltaE/T)
            P = math.exp(-delta_E / T)
            if random.random() < P:
                if len(worse_accepted) < 5:
                    worse_accepted.append({
                        "step": i,
                        "from_h": current_h,
                        "to_h": neighbor_h,
                        "delta_E": delta_E,
                        "T": round(T, 4),
                        "P": round(P, 4),
                    })
                current = neighbor
                current_h = neighbor_h

        # Resfriamento
        T = alpha * T
        steps += 1

    return current, current_h, steps, worse_accepted


def run_sa_multiple(num_runs=20, n=8, T0=100.0, alpha=0.95, max_iter=10000):
    """Executa SA múltiplas vezes para comparação."""
    results = []
    for run in range(num_runs):
        initial = tuple(random.randint(1, n) for _ in range(n))
        final_state, final_h, steps, _ = simulated_annealing(
            initial, T0=T0, alpha=alpha, max_iter=max_iter, seed=run
        )
        results.append({
            "run": run + 1,
            "final_h": final_h,
            "found": (final_h == 0),
            "steps": steps,
        })
    return results


# ============================================================
# IMPRESSÃO DOS RESULTADOS
# ============================================================

def print_separator(char="=", width=80):
    print(char * width)


def print_hill_climbing_manual():
    print_separator()
    print("HILL-CLIMBING MANUAL A PARTIR DE [1,1,1,1,1,1,1,1]")
    print_separator()

    initial = [1, 1, 1, 1, 1, 1, 1, 1]
    history, final_state, final_h, stop_reason = hill_climbing_detailed(initial)

    print(f"\nEstado inicial: {list(initial)}, h = {count_conflicts(initial)}\n")

    # Tabela resumo
    print("TABELA RESUMO DE ITERAÇÕES")
    print(f"{'Iteração':<10} {'Estado':<35} {'h(s)':<6}")
    print("-" * 55)
    for entry in history:
        print(f"{entry['iteration']:<10} {str(list(entry['state'])):<35} {entry['h']:<6}")

    # Detalhe de cada iteração
    print("\n\nDETALHE DE CADA ITERAÇÃO (Top 5 vizinhos)")
    print_separator("-")
    for entry in history:
        it = entry["iteration"]
        print(f"\n--- Iteração {it} ---")
        print(f"  Estado atual: {list(entry['state'])}, h = {entry['h']}")
        print(f"  Top 5 vizinhos:")
        print(f"  {'Vizinho':<40} {'h':<5}")
        for nb, nb_h in entry["top5_neighbors"]:
            marker = " <-- ESCOLHIDO" if nb == entry["best_neighbor"] else ""
            print(f"  {str(list(nb)):<40} {nb_h:<5}{marker}")
        print(f"  Escolhido: {list(entry['best_neighbor'])}, h = {entry['best_h']}")
        if entry['best_h'] < entry['h']:
            print(f"  Motivo: melhor vizinho com h = {entry['best_h']} < {entry['h']} (melhora)")
        elif entry['best_h'] == entry['h']:
            print(f"  Motivo: platô (melhor vizinho tem h igual ao atual)")
        else:
            print(f"  Motivo: máximo local (todos vizinhos têm h >= {entry['h']})")

    print(f"\n\nRESULTADO FINAL")
    print_separator("-")
    print(f"  Estado final: {list(final_state)}, h = {final_h}")
    print(f"  Total de iterações: {len(history)}")
    print(f"  Motivo de parada: {stop_reason}")

    if stop_reason == "local_maximum":
        print("\n  *** MÁXIMO LOCAL DETECTADO ***")
        print("  Nenhum vizinho tem h menor que o estado atual.")
        print("  A busca ficou presa; não é solução global.")
    elif stop_reason == "plateau":
        print("\n  *** PLATÔ DETECTADO ***")
        print("  Os melhores vizinhos têm h igual ao estado atual.")
    elif stop_reason == "solution":
        print("\n  *** SOLUÇÃO GLOBAL ENCONTRADA (h = 0) ***")


def print_random_restart():
    print_separator()
    print("RANDOM RESTART HILL-CLIMBING (20 execuções)")
    print_separator()

    results = random_restart_hill_climbing(num_restarts=20)

    print(f"\n{'Execução':<10} {'Estado inicial':<38} {'Passos':<8} {'h(s) final':<12} {'Solução?'}")
    print("-" * 80)
    solutions = 0
    for r in results:
        found_str = "SIM" if r["found"] else "NÃO"
        if r["found"]:
            solutions += 1
        print(f"{r['run']:<10} {str(list(r['initial'])):<38} {r['steps']:<8} {r['final_h']:<12} {found_str}")

    print(f"\nTotal de soluções encontradas: {solutions}/{len(results)}")
    avg_steps = sum(r["steps"] for r in results) / len(results)
    print(f"Média de passos: {avg_steps:.1f}")


def print_simulated_annealing():
    print_separator()
    print("SIMULATED ANNEALING")
    print_separator()

    T0 = 100.0
    alpha = 0.95
    max_iter = 10000
    initial = [1, 1, 1, 1, 1, 1, 1, 1]

    final_state, final_h, steps, worse_accepted = simulated_annealing(
        initial, T0=T0, alpha=alpha, max_iter=max_iter
    )

    print(f"\nParâmetros:")
    print(f"  Temperatura inicial (T0): {T0}")
    print(f"  Fator de resfriamento (alpha): {alpha}")
    print(f"  Política: T_nova = {alpha} * T_atual (resfriamento geométrico)")
    print(f"  Máximo de iterações: {max_iter}")

    print(f"\nResultado (partindo de {list(initial)}):")
    print(f"  Estado final: {list(final_state)}, h = {final_h}")
    print(f"  Passos realizados: {steps}")

    print(f"\nExemplos de movimentos piores aceitos:")
    print(f"{'Passo':<8} {'h_antes':<9} {'h_depois':<10} {'ΔE':<6} {'T':<10} {'P(aceitar)'}")
    print("-" * 55)
    for wa in worse_accepted:
        print(f"{wa['step']:<8} {wa['from_h']:<9} {wa['to_h']:<10} {wa['delta_E']:<6} {wa['T']:<10} {wa['P']}")

    # Múltiplas execuções para contar soluções
    print(f"\nComparação (20 execuções com estados iniciais aleatórios):")
    sa_results = run_sa_multiple(num_runs=20, T0=T0, alpha=alpha, max_iter=max_iter)
    rr_results = random_restart_hill_climbing(num_restarts=20)

    sa_solutions = sum(1 for r in sa_results if r["found"])
    rr_solutions = sum(1 for r in rr_results if r["found"])
    sa_avg_steps = sum(r["steps"] for r in sa_results) / len(sa_results)
    rr_avg_steps = sum(r["steps"] for r in rr_results) / len(rr_results)

    print(f"\n  {'Algoritmo':<30} {'Soluções':<12} {'Média passos'}")
    print(f"  {'-'*55}")
    print(f"  {'Hill-Climbing (RR)':<30} {rr_solutions}/20      {rr_avg_steps:.1f}")
    print(f"  {'Simulated Annealing':<30} {sa_solutions}/20      {sa_avg_steps:.1f}")

    print(f"\nQuantidade de soluções válidas (SA, 20 exec.): {sa_solutions}")


def print_comparison():
    print_separator()
    print("COMPARAÇÃO DOS ALGORITMOS")
    print_separator()

    # Coleta dados
    rr_results = random_restart_hill_climbing(num_restarts=20)
    sa_results = run_sa_multiple(num_runs=20)

    rr_sols = sum(1 for r in rr_results if r["found"])
    sa_sols = sum(1 for r in sa_results if r["found"])
    rr_avg_h = sum(r["final_h"] for r in rr_results) / len(rr_results)
    sa_avg_h = sum(r["final_h"] for r in sa_results) / len(sa_results)

    print(f"\n{'Critério':<35} {'Hill-Climbing (RR)':<22} {'Simulated Annealing'}")
    print("-" * 80)
    print(f"{'Qualidade (soluções/20)':<35} {rr_sols:<22} {sa_sols}")
    print(f"{'h médio final':<35} {rr_avg_h:<22.2f} {sa_avg_h:.2f}")
    print(f"{'Escapa máximos locais':<35} {'Não (reinício)':<22} {'Sim (prob.)'}")
    print(f"{'Sensível ao estado inicial':<35} {'Muito':<22} {'Moderado'}")
    print(f"{'Estabilidade':<35} {'Moderada':<22} {'Variável (T)'}")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print_hill_climbing_manual()
    print("\n\n")
    print_random_restart()
    print("\n\n")
    print_simulated_annealing()
    print("\n\n")
    print_comparison()