# GRAFOS

grafo_original = {
    'A': ['B', 'C', 'D'],
    'B': ['E', 'F'],
    'C': ['G', 'H'],
    'D': ['I'],
    'E': ['J'],
    'F': ['K', 'L'],
    'G': ['M'],
    'H': ['N', 'O'],
    'I': ['P'],
    'J': [],
    'K': ['Q'],
    'L': [],
    'M': ['R'],
    'N': [],
    'O': ['S'],
    'P': [],
    'Q': [],
    'R': [],
    'S': [],
}

grafo_modificado = {
    'A': ['B', 'C', 'D'],
    'B': ['E', 'F'],
    'C': ['H', 'G'],   # MODIFICADO
    'D': ['I'],
    'E': ['J'],
    'F': ['K', 'L'],
    'G': ['M'],
    'H': ['O', 'N'],   # MODIFICADO
    'I': ['P'],
    'J': [],
    'K': ['Q'],
    'L': [],
    'M': ['R'],
    'N': [],
    'O': ['S'],
    'P': [],
    'Q': [],
    'R': [],
    'S': [],
}

INICIO   = 'A'
OBJETIVO = 'S'

CUTOFF    = object()
NOT_FOUND = object()


# UTILITÁRIOS

class Fila:
    def __init__(self, itens=None):
        self._dados = list(itens) if itens is not None else []
        self._inicio = 0

    def __len__(self):
        return len(self._dados) - self._inicio

    def enfileirar(self, item):
        self._dados.append(item)

    def desenfileirar(self):
        if self._inicio >= len(self._dados):
            raise IndexError("fila vazia")
        item = self._dados[self._inicio]
        self._inicio += 1
        # Compacta ocasionalmente para evitar crescimento sem limite
        if self._inicio > 32 and self._inicio * 2 > len(self._dados):
            self._dados = self._dados[self._inicio:]
            self._inicio = 0
        return item

    def como_lista(self):
        return self._dados[self._inicio:]

def imprimir_tabela(passos):
    col1 = max(len("Passo"),                   max(len(str(p[0])) for p in passos))
    col2 = max(len("Nó expandido"),            max(len(str(p[1])) for p in passos))
    col3 = max(len("Fronteira após expansão"), max(len(str(p[2])) for p in passos))

    sep = f"+{'-'*(col1+2)}+{'-'*(col2+2)}+{'-'*(col3+2)}+"
    fmt = f"| {{:<{col1}}} | {{:<{col2}}} | {{:<{col3}}} |"

    print(sep)
    print(fmt.format("Passo", "Nó expandido", "Fronteira após expansão"))
    print(sep)
    for p in passos:
        print(fmt.format(str(p[0]), str(p[1]), str(p[2])))
    print(sep)


def imprimir_resultado(caminho, nos_gerados, nos_expandidos):
    print(f"  Caminho solução : {' -> '.join(caminho)}")
    print(f"  Profundidade    : {len(caminho) - 1}")
    print(f"  Custo           : {len(caminho) - 1}")
    print(f"  Nós gerados     : {nos_gerados}")
    print(f"  Nós expandidos  : {nos_expandidos}")


# BFS
# Teste de objetivo ao GERAR cada filho.
# Para imediatamente ao encontrar o objetivo - sem expandi-lo.

def bfs(grafo, inicio, objetivo):
    if inicio == objetivo:
        return [inicio], 1, 0, [(1, inicio, [])]

    fila   = Fila([inicio])
    pai    = {inicio: None}
    passos = []

    nos_gerados    = 1
    nos_expandidos = 0

    while len(fila) > 0:
        no = fila.desenfileirar()
        nos_expandidos += 1

        encontrou = False
        for vizinho in grafo[no]:
            if vizinho not in pai:
                pai[vizinho] = no
                nos_gerados += 1

                # Teste de objetivo ao gerar
                if vizinho == objetivo:
                    encontrou = True
                    break   # para sem gerar os demais filhos

                fila.enfileirar(vizinho)

        if encontrou:
            # Fronteira: fila atual (objetivo não entrou na fila)
            passos.append((nos_expandidos, no, fila.como_lista() + [objetivo]))
            caminho = []
            atual   = objetivo
            while atual is not None:
                caminho.append(atual)
                atual = pai[atual]
            caminho.reverse()
            return caminho, nos_gerados, nos_expandidos, passos

        passos.append((nos_expandidos, no, fila.como_lista()))

    return None, nos_gerados, nos_expandidos, passos


# DFS RECURSIVA
# Teste de objetivo ao GERAR cada filho.

def dfs(grafo, inicio, objetivo):
    if inicio == objetivo:
        return [inicio], 1, 0, [(1, inicio, [])]

    passos      = []
    nos_gerados = [1]
    nos_expand  = [0]
    passo_num   = [1]

    def _dfs(no, caminho, visitados):
        visitados.add(no)
        nos_expand[0] += 1

        # Filhos ainda não visitados (para mostrar na fronteira)
        fronteira = [v for v in grafo[no] if v not in visitados]
        passos.append((passo_num[0], no, fronteira))
        passo_num[0] += 1

        for vizinho in grafo[no]:
            if vizinho not in visitados:
                nos_gerados[0] += 1

                # Teste de objetivo ao gerar - retorna sem expandir S
                if vizinho == objetivo:
                    return caminho + [vizinho]

                resultado = _dfs(vizinho, caminho + [vizinho], visitados)
                if resultado is not None:
                    return resultado

        return None

    resultado = _dfs(inicio, [inicio], set())
    return resultado, nos_gerados[0], nos_expand[0], passos


# IDS RECURSIVA
# Mesma lógica da DFS com limite de profundidade.
# Ao encontrar o objetivo como filho: retorna sem expandi-lo.

def ids(grafo, inicio, objetivo):
    if inicio == objetivo:
        return [inicio], 1, 0, [], 0

    todas_passos  = []
    total_gerados = 0
    total_expand  = 0

    def _dls(no, caminho, visitados, limite, passos_iter, contadores):
        visitados.add(no)
        contadores['expandidos'] += 1

        prof_atual = len(caminho) - 1

        if prof_atual < limite:
            fronteira = [v for v in grafo[no] if v not in visitados]
        else:
            fronteira = ['(limite)'] if grafo[no] else []

        passos_iter.append((contadores['passo'], no, fronteira))
        contadores['passo'] += 1

        # Nó no limite: não gera filhos
        if prof_atual >= limite:
            return CUTOFF if grafo[no] else NOT_FOUND

        resultado_final = NOT_FOUND

        for vizinho in grafo[no]:
            if vizinho not in visitados:
                contadores['gerados'] += 1

                # Teste de objetivo ao gerar - retorna sem expandir S
                if vizinho == objetivo:
                    return caminho + [vizinho]

                sub = _dls(vizinho, caminho + [vizinho], visitados,
                           limite, passos_iter, contadores)

                if sub is not CUTOFF and sub is not NOT_FOUND:
                    return sub

                if sub is CUTOFF:
                    resultado_final = CUTOFF

        return resultado_final

    limite = 0
    while True:
        passos_iter = []
        contadores  = {'gerados': 1, 'expandidos': 0, 'passo': 1}
        visitados   = set()

        resultado = _dls(inicio, [inicio], visitados, limite,
                         passos_iter, contadores)

        total_gerados += contadores['gerados']
        total_expand  += contadores['expandidos']
        todas_passos.append((limite, passos_iter))

        if resultado is not CUTOFF and resultado is not NOT_FOUND:
            return resultado, total_gerados, total_expand, todas_passos, limite

        if resultado is NOT_FOUND:
            return None, total_gerados, total_expand, todas_passos, limite

        limite += 1


# EXECUÇÃO E EXIBIÇÃO

def executar_e_exibir(nome_grafo, grafo):
    sep = "=" * 70
    print(f"\n{sep}")
    print(f"  GRAFO: {nome_grafo}")
    print(sep)

    print(f"\n{'─'*70}")
    print("  BUSCA EM AMPLITUDE (BFS)")
    print(f"{'─'*70}")
    caminho, gerados, expandidos, passos = bfs(grafo, INICIO, OBJETIVO)
    print()
    imprimir_tabela(passos)
    print()
    imprimir_resultado(caminho, gerados, expandidos)

    print(f"\n{'─'*70}")
    print("  BUSCA EM PROFUNDIDADE (DFS)")
    print(f"{'─'*70}")
    caminho, gerados, expandidos, passos = dfs(grafo, INICIO, OBJETIVO)
    print()
    imprimir_tabela(passos)
    print()
    imprimir_resultado(caminho, gerados, expandidos)

    print(f"\n{'─'*70}")
    print("  BUSCA ITERATIVA EM PROFUNDIDADE (IDS)")
    print(f"{'─'*70}")
    caminho, gerados, expandidos, todas_passos, lim_final = ids(grafo, INICIO, OBJETIVO)
    for (limite, passos_iter) in todas_passos:
        print(f"\n  >> Iteração com limite = {limite}:")
        imprimir_tabela(passos_iter)
    print(f"\n  Limite onde a solução foi encontrada: {lim_final}")
    print()
    imprimir_resultado(caminho, gerados, expandidos)


def comparar_resultados():
    sep = "=" * 70
    print(f"\n{sep}")
    print("  COMPARAÇÃO: GRAFO ORIGINAL vs. GRAFO MODIFICADO")
    print(sep)

    col = 22
    print(f"\n{'Algoritmo':<10} {'Métrica':<22} {'Original':>{col}} {'Modificado':>{col}}")
    print("-" * 78)

    for algo, fn in [("BFS", bfs), ("DFS", dfs), ("IDS", ids)]:
        orig = fn(grafo_original,  INICIO, OBJETIVO)
        mod  = fn(grafo_modificado, INICIO, OBJETIVO)
        for idx, metrica in enumerate(["Caminho", "Nós gerados", "Nós expandidos"]):
            if metrica == "Caminho":
                v_o = " -> ".join(orig[0])
                v_m = " -> ".join(mod[0])
            elif metrica == "Nós gerados":
                v_o, v_m = str(orig[1]), str(mod[1])
            else:
                v_o, v_m = str(orig[2]), str(mod[2])
            prefixo = f"  {algo}" if idx == 0 else ""
            print(f"{prefixo:<10} {metrica:<22} {v_o:>{col}} {v_m:>{col}}")
        print()


if __name__ == "__main__":
    executar_e_exibir("ORIGINAL", grafo_original)
    executar_e_exibir("MODIFICADO (C: H,G | H: O,N)", grafo_modificado)
    comparar_resultados()