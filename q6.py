import math
import random
import copy

LINHAS = 4
COLUNAS = 4
VERMELHO = 1
AMARELO = 2

def fazer_tabuleiro_inicial():
    tabuleiro = [[0]*COLUNAS for _ in range(LINHAS)]
    # V em [3,0] e [2,1]; A em [2,0] e [3,1]
    tabuleiro[3][0] = VERMELHO
    tabuleiro[2][1] = VERMELHO
    tabuleiro[2][0] = AMARELO
    tabuleiro[3][1] = AMARELO
    return tabuleiro

def soltar_peca(tabuleiro, coluna, jogador):
    t = copy.deepcopy(tabuleiro)
    for linha in range(LINHAS-1, -1, -1):
        if t[linha][coluna] == 0:
            t[linha][coluna] = jogador
            return t, linha
    return None, -1  # coluna cheia

def eh_coluna_valida(tabuleiro, coluna):
    return tabuleiro[0][coluna] == 0

def obter_colunas_validas(tabuleiro):
    return [c for c in range(COLUNAS) if eh_coluna_valida(tabuleiro, c)]

def verificar_vencedor(tabuleiro):
    # horizontal
    for r in range(LINHAS):
        for c in range(COLUNAS-3):
            p = tabuleiro[r][c]
            if p != 0 and all(tabuleiro[r][c+i] == p for i in range(4)):
                return p
    # vertical
    for r in range(LINHAS-3):
        for c in range(COLUNAS):
            p = tabuleiro[r][c]
            if p != 0 and all(tabuleiro[r+i][c] == p for i in range(4)):
                return p
    # diagonal \
    for r in range(LINHAS-3):
        for c in range(COLUNAS-3):
            p = tabuleiro[r][c]
            if p != 0 and all(tabuleiro[r+i][c+i] == p for i in range(4)):
                return p
    # diagonal /
    for r in range(3, LINHAS):
        for c in range(COLUNAS-3):
            p = tabuleiro[r][c]
            if p != 0 and all(tabuleiro[r-i][c+i] == p for i in range(4)):
                return p
    return 0

def eh_terminal(tabuleiro):
    return verificar_vencedor(tabuleiro) != 0 or len(obter_colunas_validas(tabuleiro)) == 0

def imprimir_tabuleiro(tabuleiro):
    for linha in tabuleiro:
        print(' '.join(['.','V','A'][c] for c in linha))
    print()

#  POLITICAS DE ROLLOUT (SIMULACAO)
def simulacao_aleatoria(tabuleiro, jogador):
    t = copy.deepcopy(tabuleiro)
    atual = jogador
    while not eh_terminal(t):
        colunas = obter_colunas_validas(t)
        coluna = random.choice(colunas)
        t, _ = soltar_peca(t, coluna, atual)
        atual = AMARELO if atual == VERMELHO else VERMELHO
    v = verificar_vencedor(t)
    if v == VERMELHO: return 1
    if v == AMARELO: return -1
    return 0

def simulacao_semi_gananciosa(tabuleiro, jogador):
    t = copy.deepcopy(tabuleiro)
    atual = jogador
    prioridade_centro = [1, 3, 0, 2]  # prefere cols 1,3 depois 0,2
    while not eh_terminal(t):
        colunas = obter_colunas_validas(t)
        # 1. Verifica se o jogador atual pode vencer imediatamente
        for c in colunas:
            nt, _ = soltar_peca(t, c, atual)
            if nt and verificar_vencedor(nt) == atual:
                t = nt
                atual = AMARELO if atual == VERMELHO else VERMELHO
                break
        else:
            # 2. Bloqueia vitoria imediata do oponente
            oponente = AMARELO if atual == VERMELHO else VERMELHO
            bloqueado = False
            for c in colunas:
                nt, _ = soltar_peca(t, c, oponente)
                if nt and verificar_vencedor(nt) == oponente:
                    t, _ = soltar_peca(t, c, atual)
                    atual = AMARELO if atual == VERMELHO else VERMELHO
                    bloqueado = True
                    break
            if not bloqueado:
                # 3. Prefere colunas centrais
                for c in prioridade_centro:
                    if c in colunas:
                        t, _ = soltar_peca(t, c, atual)
                        atual = AMARELO if atual == VERMELHO else VERMELHO
                        break
    v = verificar_vencedor(t)
    if v == VERMELHO: return 1
    if v == AMARELO: return -1
    return 0

#  NODO MCTS
class NodoMCTS:
    def __init__(self, tabuleiro, jogador, pai=None, movimento=None):
        self.tabuleiro = tabuleiro
        self.jogador = jogador      # jogador de quem e a vez
        self.pai = pai
        self.movimento = movimento  # coluna que levou aqui
        self.filhos = []
        self.N = 0                  # visitas
        self.W = 0                  # vitorias (perspectiva do VERMELHO)
        self.nao_tentados = obter_colunas_validas(tabuleiro)
        random.shuffle(self.nao_tentados)

    def esta_totalmente_expandido(self):
        return len(self.nao_tentados) == 0

    def melhor_filho(self, C):
        return max(self.filhos,
                   key=lambda c: (c.W/c.N) + C*math.sqrt(math.log(self.N)/c.N))

    def valores_uct(self, C):
        valores = {}
        for f in self.filhos:
            exploit = f.W / f.N
            explore = C * math.sqrt(math.log(self.N) / f.N)
            valores[f.movimento] = (exploit + explore, exploit, explore)
        return valores

#  ALGORITMO MCTS
def mcts(tabuleiro_raiz, jogador_raiz, n_iter, C=1.4, fn_rollout=simulacao_aleatoria, detalhado=False):
    raiz = NodoMCTS(tabuleiro_raiz, jogador_raiz)

    log_iteracao = []

    for it in range(1, n_iter+1):
        # SELECAO
        nodo = raiz
        caminho = []
        while nodo.esta_totalmente_expandido() and nodo.filhos and not eh_terminal(nodo.tabuleiro):
            nodo = nodo.melhor_filho(C)
            caminho.append(nodo.movimento)

        # EXPANSAO
        movimento_expandido = None
        if not eh_terminal(nodo.tabuleiro) and nodo.nao_tentados:
            col = nodo.nao_tentados.pop()
            novo_tabuleiro, _ = soltar_peca(nodo.tabuleiro, col, nodo.jogador)
            proximo_jogador = AMARELO if nodo.jogador == VERMELHO else VERMELHO
            filho = NodoMCTS(novo_tabuleiro, proximo_jogador, pai=nodo, movimento=col)
            nodo.filhos.append(filho)
            nodo = filho
            movimento_expandido = col
            caminho.append(col)

        # ROLLOUT
        resultado = fn_rollout(nodo.tabuleiro, nodo.jogador)
        # BACKPROP
        n = nodo
        while n is not None:
            n.N += 1
            # W conta vitorias para VERMELHO
            if resultado == 1:
                n.W += 1
            n = n.pai

        if detalhado:
            # captura estatisticas dos filhos da raiz
            estats = {f.movimento: (f.N, f.W) for f in raiz.filhos}
            uct = raiz.valores_uct(C)
            log_iteracao.append({'iter': it, 'caminho': list(caminho), 'expandido': movimento_expandido, 'resultado': resultado, 'estats': copy.deepcopy(estats), 'uct': copy.deepcopy(uct),
            })

    return raiz, log_iteracao

#  SEMENTE DETERMINISTICA PARA REPRODUTIBILIDADE
random.seed(42)

TABULEIRO_INICIAL = fazer_tabuleiro_inicial()
print("Tabuleiro Inicial")
imprimir_tabuleiro(TABULEIRO_INICIAL)

#  10 ITERACOES DETALHADAS (C=1.4, rollout aleatorio)
random.seed(42)
raiz14, log14 = mcts(TABULEIRO_INICIAL, VERMELHO, 10, C=1.4, fn_rollout=simulacao_aleatoria, detalhado=True)

print("10 Iteracoes (C=1.4, Simulacao Aleatoria)")
for entrada in log14:
    it = entrada['iter']
    caminho_str = ' -> '.join([f'c{c+1}' for c in entrada['caminho']]) if entrada['caminho'] else 'raiz'
    exp_str = f"c{entrada['expandido']+1}" if entrada['expandido'] is not None else 'nenhum'
    res_str = {1:'VERMELHO vence', -1:'AMARELO vence', 0:'empate'}[entrada['resultado']]
    print(f"\nIteracao {it}:")
    print(f"  Caminho selecionado: {caminho_str}")
    print(f"  Nodo expandido: {exp_str}")
    print(f"  Resultado do rollout: {res_str}")
    print(f"  Estatisticas dos filhos da raiz (N, W):")
    for col in sorted(entrada['estats'].keys()):
        n, w = entrada['estats'][col]
        print(f"    c{col+1}: N={n}, W={w}", end='')
        if col in entrada['uct']:
            val_uct, exploit, explore = entrada['uct'][col]
            print(f"  UCT={val_uct:.4f} (exploit={exploit:.4f}, explore={explore:.4f})", end='')
        print()

# Tabela Final
print("\nTabela Final (C=1.4)")
print(f"{'Jogada':<8} {'Visitas':>8} {'Vitorias':>10} {'UCT':>10}")
for f in sorted(raiz14.filhos, key=lambda x: x.movimento):
    N_total = raiz14.N
    if f.N > 0:
        exploit = f.W / f.N
        explore = 1.4 * math.sqrt(math.log(N_total) / f.N)
        uct = exploit + explore
    else:
        uct = float('inf')
    print(f"c{f.movimento+1:<7} {f.N:>8} {f.W:>10} {uct:>10.4f}")

#  COMPARAR VALORES DE C (200 iteracoes cada)
print("\nComparacao de Valores C (200 iteracoes, rollout aleatorio)")
resultados_C = {}
for val_C in [0.1, 1.4, 3.0]:
    random.seed(42)
    raiz_c, _ = mcts(TABULEIRO_INICIAL, VERMELHO, 200, C=val_C, fn_rollout=simulacao_aleatoria, detalhado=False)
    visitas_coluna = {f.movimento: (f.N, f.W) for f in raiz_c.filhos}
    melhor = max(raiz_c.filhos, key=lambda x: x.N).movimento
    resultados_C[val_C] = {'visitas': visitas_coluna, 'melhor': melhor, 'raiz_N': raiz_c.N}
    print(f"\nC={val_C}:")
    print(f"  Melhor jogada: c{melhor+1}")
    total_filhos = sum(f.N for f in raiz_c.filhos)
    for col in sorted(visitas_coluna.keys()):
        n, w = visitas_coluna[col]
        print(f"  c{col+1}: N={n}, W={w}, frac={n/total_filhos:.3f}")

#  COMPARAR TIPOS DE ROLLOUT (200 iteracoes, C=1.4)
print("\nComparacao de Rollout (200 iteracoes, C=1.4)")
for rotulo, fn in [('Aleatorio', simulacao_aleatoria), ('Semi-Ganancioso', simulacao_semi_gananciosa)]:
    random.seed(42)
    raiz_r, _ = mcts(TABULEIRO_INICIAL, VERMELHO, 200, C=1.4, fn_rollout=fn, detalhado=False)
    melhor = max(raiz_r.filhos, key=lambda x: x.N).movimento
    print(f"\n{rotulo}:")
    print(f"  Melhor jogada: c{melhor+1}")
    for f in sorted(raiz_r.filhos, key=lambda x: x.movimento):
        wr = f.W/f.N if f.N > 0 else 0
        print(f"  c{f.movimento+1}: N={f.N}, W={f.W}, WR={wr:.3f}")

#  CONVERGENCIA: iteracoes necessarias para estabilizar
print("\nAnalise de Convergencia")
for rotulo, fn in [('Aleatorio', simulacao_aleatoria), ('Semi-Ganancioso', simulacao_semi_gananciosa)]:
    melhor_anterior = None
    estabilizado_em = None
    for n_it in [10, 25, 50, 100, 200, 500]:
        random.seed(42)
        raiz_conv, _ = mcts(TABULEIRO_INICIAL, VERMELHO, n_it, C=1.4, fn_rollout=fn, detalhado=False)
        melhor = max(raiz_conv.filhos, key=lambda x: x.N).movimento
        print(f"  {rotulo} | iter={n_it:4d} | melhor=c{melhor+1}")