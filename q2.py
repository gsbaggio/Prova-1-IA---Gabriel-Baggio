import heapq # esse importa é para a fila de prioridade, para ver primeiro os nós de menor custo f(n)

# Definicao do grafo
GRAFO = {
    'A': [('B', 2), ('C', 4), ('D', 3)],
    'B': [('E', 3), ('F', 5)],
    'C': [('G', 4), ('H', 6)],
    'D': [('I', 2)],
    'E': [('J', 4)],
    'F': [('K', 3), ('L', 5)],
    'G': [('M', 6)],
    'H': [('N', 3), ('O', 4)],
    'I': [('P', 5)],
    'J': [('Q', 4)],
    'K': [('R', 3)],
    'L': [],
    'M': [('S', 2)],
    'N': [],
    'O': [('T', 5)],
    'P': [],
    'Q': [],
    'R': [('T', 4)],
    'S': [('T', 3)],
    'T': [],
}

# Heuristicas originais
HEURISTICA_ORIGINAL = {
    'A': 10, 'B': 8,  'C': 7,  'D': 9,
    'E': 6,  'F': 5,  'G': 6,  'H': 4,
    'I': 7,  'J': 5,  'K': 3,  'L': 6,
    'M': 3,  'N': 4,  'O': 1,  'P': 8,
    'Q': 4,  'R': 2,  'S': 1,  'T': 0,
}

# Heuristicas modificadas (3 nos alterados: O, S, R)
HEURISTICA_MODIFICADA = dict(HEURISTICA_ORIGINAL)
HEURISTICA_MODIFICADA['O'] = 10   # era 1  -> aumentado para desfavorecer esse ramo
HEURISTICA_MODIFICADA['S'] = 10   # era 1  -> aumentado
HEURISTICA_MODIFICADA['R'] = 1    # era 2  -> diminuido para favorecer esse ramo

INICIO = 'A'
OBJETIVO  = 'T'


# Utilitarios

def reconstruir_caminho(veio_de, nodo):
    # Reconstroi o caminho do inicio ate 'nodo' usando o dicionario veio_de.
    caminho = []
    while nodo is not None:
        caminho.append(nodo)
        nodo = veio_de[nodo]
    caminho.reverse()
    return caminho


def custo_caminho(grafo, caminho):
    # Calcula o custo total de um caminho.
    total = 0
    for i in range(len(caminho) - 1):
        u, v = caminho[i], caminho[i + 1]
        for vizinho, custo in grafo[u]:
            if vizinho == v:
                total += custo
                break
    return total


def str_fronteira(fronteira):
    # Formata a fronteira para exibicao.
    items = [(nodo, valor_f) for valor_f, _, nodo in fronteira]
    items.sort(key=lambda x: x[1])
    return ', '.join(f'{n}:{v}' for n, v in items)


# Greedy Best-First Search

def busca_gulosa(grafo, inicio, objetivo, heuristica, rotulo="ORIGINAL"):
    # Busca Gulosa pela Melhor Escolha.
    # f(n) = h(n)

    print(f"GREEDY BEST-FIRST SEARCH - Heuristica: {rotulo}")
    print(f"{'Passo':<6} {'Expandido':<10} {'h(n)':<6} "
          f"{'Fronteira (no:h)':<40} {'Caminho parcial'}")

    # Fronteira: (h(n), contador, no)
    # contador serve como desempate deterministico
    contador = 0
    fronteira = []
    heapq.heappush(fronteira, (heuristica[inicio], contador, inicio))

    veio_de    = {inicio: None}
    expandidos     = []
    gerados    = {inicio}
    passo         = 0
    visitados      = set()

    while fronteira:
        valor_h, _, nodo = heapq.heappop(fronteira)

        if nodo in visitados:
            continue
        visitados.add(nodo)

        passo += 1
        expandidos.append(nodo)
        caminho_parcial = ' -> '.join(reconstruir_caminho(veio_de, nodo))

        if nodo == objetivo:
            exibicao_fronteira = ', '.join(
                f"{n}:{heuristica[n]}"
                for _, __, n in sorted(fronteira)
                if n not in visitados
            )
            print(f"{passo:<6} {nodo:<10} {valor_h:<6} {exibicao_fronteira:<40} {caminho_parcial}")
            caminho = reconstruir_caminho(veio_de, nodo)
            custo = custo_caminho(grafo, caminho)
            print(f"\nRESULTADO")
            print(f"Caminho: {' -> '.join(caminho)}")
            print(f"Custo total:       {custo}")
            print(f"Nos gerados:       {len(gerados)}")
            print(f"Nos expandidos:    {len(expandidos)}")
            return caminho, custo, len(gerados), len(expandidos)

        for vizinho, _ in grafo[nodo]:
            if vizinho not in visitados and vizinho not in veio_de:
                contador += 1
                veio_de[vizinho] = nodo
                gerados.add(vizinho)
                heapq.heappush(fronteira, (heuristica[vizinho], contador, vizinho))

        # Formata fronteira DEPOIS de expandir
        exibicao_fronteira = ', '.join(
            f"{n}:{heuristica[n]}"
            for _, __, n in sorted(fronteira)
            if n not in visitados
        )

        print(f"{passo:<6} {nodo:<10} {valor_h:<6} {exibicao_fronteira:<40} {caminho_parcial}")

    print("Sem solucao encontrada.")
    return None, float('inf'), len(gerados), len(expandidos)


# A*

def busca_a_estrela(grafo, inicio, objetivo, heuristica, rotulo="ORIGINAL"):
    # Busca A*.
    # f(n) = g(n) + h(n)

    print(f"A* - Heuristica: {rotulo}")
    print(f"{'Passo':<6} {'No':<6} {'g(n)':<6} {'h(n)':<6} {'f(n)':<6} "
          f"{'Fronteira ordenada por f':<45} {'Caminho parcial'}")

    # Fronteira: (f, g, contador, no)
    contador  = 0
    fronteira = []
    heapq.heappush(fronteira, (heuristica[inicio], 0, contador, inicio))

    veio_de = {inicio: None}
    custo_g   = {inicio: 0}
    expandidos  = []
    gerados = {inicio}
    passo      = 0
    visitados   = set()

    while fronteira:
        valor_f, valor_g, _, nodo = heapq.heappop(fronteira)

        if nodo in visitados:
            continue
        visitados.add(nodo)

        passo += 1
        expandidos.append(nodo)
        valor_h       = heuristica[nodo]
        caminho_parcial = ' -> '.join(reconstruir_caminho(veio_de, nodo))

        # Fronteira para exibicao (sem visitados, ordenada por f)
        itens_fronteira = sorted(
            [(fn, n) for fn, _g, _c, n in fronteira if n not in visitados]
        )
        exibicao_fronteira = ', '.join(f"{n}:{fn}" for fn, n in itens_fronteira[:6])
        if len(itens_fronteira) > 6:
            exibicao_fronteira += '...'

        print(f"{passo:<6} {nodo:<6} {valor_g:<6} {valor_h:<6} {valor_f:<6} "
              f"{exibicao_fronteira:<45} {caminho_parcial}")

        if nodo == objetivo:
            caminho = reconstruir_caminho(veio_de, nodo)
            custo = custo_g[objetivo]
            print(f"\nRESULTADO")
            print(f"Caminho: {' -> '.join(caminho)}")
            print(f"Custo total:       {custo}")
            print(f"Nos gerados:       {len(gerados)}")
            print(f"Nos expandidos:    {len(expandidos)}")
            return caminho, custo, len(gerados), len(expandidos)

        for vizinho, custo_aresta in grafo[nodo]:
            novo_g = custo_g[nodo] + custo_aresta
            if vizinho not in custo_g or novo_g < custo_g[vizinho]:
                custo_g[vizinho]   = novo_g
                veio_de[vizinho] = nodo
                novo_f = novo_g + heuristica[vizinho]
                contador += 1
                gerados.add(vizinho)
                heapq.heappush(fronteira, (novo_f, novo_g, contador, vizinho))

    print("Sem solucao encontrada.")
    return None, float('inf'), len(gerados), len(expandidos)


# Tabela resumo comparativa
def imprimir_tabela_comparacao(resultados):
    # resultados: lista de dicts com chaves:
    #   algorithm, heuristica, caminho, custo, gerados, expandidos

    print("TABELA COMPARATIVA")
    header = f"{'Algoritmo':<12} {'Heuristica':<12} {'Caminho':<35} {'Custo':<7} {'Gerados':<9} {'Expandidos'}"
    print(header)
    for r in resultados:
        path_str = ' -> '.join(r['caminho']) if r['caminho'] else 'N/A'
        print(f"{r['algorithm']:<12} {r['heuristica']:<12} {path_str:<35} "
              f"{r['custo']:<7} {r['gerados']:<9} {r['expandidos']}")

resultados = []

# --- Heuristica original ---
g_caminho_o, g_custo_o, g_ger_o, g_exp_o = busca_gulosa(
    GRAFO, INICIO, OBJETIVO, HEURISTICA_ORIGINAL, "ORIGINAL")

a_caminho_o, a_custo_o, a_ger_o, a_exp_o = busca_a_estrela(
    GRAFO, INICIO, OBJETIVO, HEURISTICA_ORIGINAL, "ORIGINAL")

resultados.append({'algorithm': 'Greedy', 'heuristica': 'Original',
                'caminho': g_caminho_o, 'custo': g_custo_o,
                'gerados': g_ger_o, 'expandidos': g_exp_o})
resultados.append({'algorithm': 'A*', 'heuristica': 'Original',
                'caminho': a_caminho_o, 'custo': a_custo_o,
                'gerados': a_ger_o, 'expandidos': a_exp_o})

# --- Heuristica modificada ---
print("\n\nNos com heuristica modificada:")
print("    O: 1 -> 10  |  S: 1 -> 10  |  R: 2 -> 1")

g_caminho_m, g_custo_m, g_ger_m, g_exp_m = busca_gulosa(
    GRAFO, INICIO, OBJETIVO, HEURISTICA_MODIFICADA, "MODIFICADA")

a_caminho_m, a_custo_m, a_ger_m, a_exp_m = busca_a_estrela(
    GRAFO, INICIO, OBJETIVO, HEURISTICA_MODIFICADA, "MODIFICADA")

resultados.append({'algorithm': 'Greedy', 'heuristica': 'Modificada',
                'caminho': g_caminho_m, 'custo': g_custo_m,
                'gerados': g_ger_m, 'expandidos': g_exp_m})
resultados.append({'algorithm': 'A*', 'heuristica': 'Modificada',
                'caminho': a_caminho_m, 'custo': a_custo_m,
                'gerados': a_ger_m, 'expandidos': a_exp_m})

# --- Tabela comparativa ---
imprimir_tabela_comparacao(resultados)

# --- Analise ---
res_original = (
    {'caminho': g_caminho_o, 'custo': g_custo_o,
        'gerados': g_ger_o, 'expandidos': g_exp_o},
    {'caminho': a_caminho_o, 'custo': a_custo_o,
        'gerados': a_ger_o, 'expandidos': a_exp_o},
)
res_modificado = (
    {'caminho': g_caminho_m, 'custo': g_custo_m,
        'gerados': g_ger_m, 'expandidos': g_exp_m},
    {'caminho': a_caminho_m, 'custo': a_custo_m,
        'gerados': a_ger_m, 'expandidos': a_exp_m},
)