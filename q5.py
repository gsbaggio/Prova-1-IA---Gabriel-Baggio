import math
import string


# ESTRUTURA DA ARVORE

FOLHAS = {
    'E': [3, 5],
    'F': [6, 9],
    'G': [1, 2],
    'H': [0, -1],
    'I': [7, 4],
    'J': [5, 6],
}

FILHOS = {
    'A': ['B', 'C', 'D'],
    'B': ['E', 'F'],
    'C': ['G', 'H'],
    'D': ['I', 'J'],
}

HEURISTICA = {'E': 4, 'F': 7, 'G': 2, 'H': 5, 'I': 6, 'J': 1}


# ALGORITMO 1: MINIMAX COMPLETO
def minimax(no, eh_max, folhas=FOLHAS, filhos=FILHOS):
    # Minimax sem limite de profundidade.
    if no in folhas:
        valor = max(folhas[no]) if eh_max else min(folhas[no])
        return valor
    valores = [minimax(c, not eh_max, folhas, filhos)
              for c in filhos[no]]
    return max(valores) if eh_max else min(valores)


def minimax_rastreio_completo(folhas=FOLHAS, filhos=FILHOS):
    # Executa Minimax e retorna valores de todos os nos.
    resultados = {}

    def _mm(no, eh_max):
        if no in folhas:
            valor = max(folhas[no]) if eh_max else min(folhas[no])
            resultados[no] = ('MAX' if eh_max else 'MIN', valor)
            return valor
        valores = [_mm(c, not eh_max) for c in filhos[no]]
        valor = max(valores) if eh_max else min(valores)
        resultados[no] = ('MAX' if eh_max else 'MIN', valor)
        return valor

    valor_raiz = _mm('A', True)
    return valor_raiz, resultados


# ALGORITMO 2: ALPHA-BETA
def alpha_beta(no, eh_max, alpha, beta,
               folhas=FOLHAS, filhos=FILHOS,
               estatisticas=None, profundidade=0):
    # Poda Alpha-Beta. estatisticas e' um dict mutavel para contagens.
    if estatisticas is None:
        estatisticas = {'nos': 0, 'podas': 0, 'nos_podados': []}

    estatisticas['nos'] += 1

    if no in folhas:
        valor = max(folhas[no]) if eh_max else min(folhas[no])
        return valor, estatisticas

    if eh_max:
        valor = -math.inf
        for filho in filhos[no]:
            valor_filho, estatisticas = alpha_beta(
                filho, False, alpha, beta, folhas, filhos, estatisticas, profundidade + 1)
            valor = max(valor, valor_filho)
            alpha = max(alpha, valor)
            if beta <= alpha:
                estatisticas['podas'] += 1
                restantes = filhos[no][filhos[no].index(filho) + 1:]
                estatisticas['nos_podados'].extend(restantes)
                break
    else:
        valor = math.inf
        for filho in filhos[no]:
            valor_filho, estatisticas = alpha_beta(
                filho, True, alpha, beta, folhas, filhos, estatisticas, profundidade + 1)
            valor = min(valor, valor_filho)
            beta = min(beta, valor)
            if beta <= alpha:
                estatisticas['podas'] += 1
                restantes = filhos[no][filhos[no].index(filho) + 1:]
                estatisticas['nos_podados'].extend(restantes)
                break

    return valor, estatisticas


def alpha_beta_rastreio_passo(folhas=FOLHAS, filhos=FILHOS):
    # Retorna tabela passo a passo do Alpha-Beta.
    passos = []
    passo = [0]

    def _ab(no, eh_max, alpha, beta):
        passo[0] += 1
        alfa_str = str(alpha) if alpha != -math.inf else '-inf'
        beta_str = str(beta) if beta != math.inf else '+inf'

        if no in folhas:
            valor = max(folhas[no]) if eh_max else min(folhas[no])
            passos.append({
                'passo': passo[0],
                'no': no,
                'tipo': 'MAX' if eh_max else 'MIN',
                'alpha': alfa_str,
                'beta': beta_str,
                'value': valor,
                'podado': 'nao',
            })
            return valor

        if eh_max:
            valor = -math.inf
            for filho in filhos[no]:
                passos.append({
                    'passo': passo[0],
                    'no': no,
                    'tipo': 'MAX',
                    'alpha': alfa_str,
                    'beta': beta_str,
                    'value': '?',
                    'podado': 'nao',
                })
                passo[0] += 1
                alfa_str = str(alpha) if alpha != -math.inf else '-inf'
                beta_str = str(beta) if beta != math.inf else '+inf'
                valor_filho = _ab(filho, False, alpha, beta)
                valor = max(valor, valor_filho)
                alpha = max(alpha, valor)
                alfa_str = str(alpha) if alpha != -math.inf else '-inf'
                if beta <= alpha:
                    rest = filhos[no][filhos[no].index(filho) + 1:]
                    for r in rest:
                        passo[0] += 1
                        passos.append({
                            'passo': passo[0],
                            'no': r,
                            'tipo': '---',
                            'alpha': alfa_str,
                            'beta': beta_str,
                            'value': '---',
                            'podado': 'SIM',
                        })
                    break
        else:
            valor = math.inf
            for filho in filhos[no]:
                passos.append({
                    'passo': passo[0],
                    'no': no,
                    'tipo': 'MIN',
                    'alpha': alfa_str,
                    'beta': beta_str,
                    'value': '?',
                    'podado': 'nao',
                })
                passo[0] += 1
                alfa_str = str(alpha) if alpha != -math.inf else '-inf'
                beta_str = str(beta) if beta != math.inf else '+inf'
                valor_filho = _ab(filho, True, alpha, beta)
                valor = min(valor, valor_filho)
                beta = min(beta, valor)
                beta_str = str(beta) if beta != math.inf else '+inf'
                if beta <= alpha:
                    rest = filhos[no][filhos[no].index(filho) + 1:]
                    for r in rest:
                        passo[0] += 1
                        passos.append({
                            'passo': passo[0],
                            'no': r,
                            'tipo': '---',
                            'alpha': alfa_str,
                            'beta': beta_str,
                            'value': '---',
                            'podado': 'SIM',
                        })
                    break
        return valor

    valor_raiz = _ab('A', True, -math.inf, math.inf)
    return valor_raiz, passos


def alpha_beta_rastreio_compacto(folhas=FOLHAS, filhos=FILHOS):
    # Tabela compacta: cada no aparece uma vez e inclui folhas/podas.
    passos = []
    passo = [0]

    letras = list(string.ascii_uppercase)
    proximo_idx_folha = [letras.index('K')]
    rotulos_folha = {}

    def _atribuir_rotulos(no):
        if no in folhas:
            for i, _ in enumerate(folhas[no]):
                rotulos_folha[(no, i)] = letras[proximo_idx_folha[0]]
                proximo_idx_folha[0] += 1
            return
        for filho in filhos[no]:
            _atribuir_rotulos(filho)

    _atribuir_rotulos('A')

    def _alpha_str(a):
        return str(a) if a != -math.inf else '-inf'

    def _beta_str(b):
        return str(b) if b != math.inf else '+inf'

    def _adicionar_linha(node_label, node_type, alpha, beta, podado):
        passo[0] += 1
        passos.append({
            'passo': passo[0],
            'no': node_label,
            'tipo': node_type,
            'alpha': _alpha_str(alpha),
            'beta': _beta_str(beta),
            'podado': 'SIM' if podado else 'nao',
        })

    def _adicionar_subarvore_podada(no, alpha, beta):
        _adicionar_linha(no, '---', alpha, beta, True)
        if no in folhas:
            for i, _ in enumerate(folhas[no]):
                _adicionar_linha(rotulos_folha[(no, i)], 'FOLHA', alpha, beta, True)
            return
        for filho in filhos[no]:
            _adicionar_subarvore_podada(filho, alpha, beta)

    def _avaliar_valores_folha(no, eh_max, alpha, beta):
        valor = -math.inf if eh_max else math.inf
        for i, leaf_val in enumerate(folhas[no]):
            _adicionar_linha(rotulos_folha[(no, i)], 'FOLHA', alpha, beta, False)
            if eh_max:
                valor = max(valor, leaf_val)
                alpha = max(alpha, valor)
            else:
                valor = min(valor, leaf_val)
                beta = min(beta, valor)

            if beta <= alpha:
                restantes = range(i + 1, len(folhas[no]))
                for r in restantes:
                    _adicionar_linha(rotulos_folha[(no, r)], 'FOLHA', alpha, beta, True)
                break
        return valor

    def _ab(no, eh_max, alpha, beta):
        _adicionar_linha(no, 'MAX' if eh_max else 'MIN', alpha, beta, False)

        if no in folhas:
            return _avaliar_valores_folha(no, eh_max, alpha, beta)

        if eh_max:
            valor = -math.inf
            for filho in filhos[no]:
                valor_filho = _ab(filho, False, alpha, beta)
                valor = max(valor, valor_filho)
                alpha = max(alpha, valor)
                if beta <= alpha:
                    restantes = filhos[no][filhos[no].index(filho) + 1:]
                    for r in restantes:
                        _adicionar_subarvore_podada(r, alpha, beta)
                    break
        else:
            valor = math.inf
            for filho in filhos[no]:
                valor_filho = _ab(filho, True, alpha, beta)
                valor = min(valor, valor_filho)
                beta = min(beta, valor)
                if beta <= alpha:
                    restantes = filhos[no][filhos[no].index(filho) + 1:]
                    for r in restantes:
                        _adicionar_subarvore_podada(r, alpha, beta)
                    break
        return valor

    valor_raiz = _ab('A', True, -math.inf, math.inf)
    return valor_raiz, passos


# ALGORITMO 3: MINIMAX COM PROFUNDIDADE LIMITADA
def minimax_limitado(no, eh_max, limite_profundidade, profundidade_atual=0,
                    folhas=FOLHAS, filhos=FILHOS, heuristica=HEURISTICA):
    # Minimax com corte de profundidade e funcao heuristica.
    # Se e' no terminal (folha real)
    if no in folhas and profundidade_atual > limite_profundidade:
        valor = max(folhas[no]) if eh_max else min(folhas[no])
        return valor

    # Se atingiu limite de profundidade, usa heuristica
    if profundidade_atual >= limite_profundidade:
        return heuristica.get(no, 0)

    if no not in filhos:
        # No folha dentro do limite
        valor = max(folhas[no]) if eh_max else min(folhas[no])
        return valor

    valores = [minimax_limitado(c, not eh_max, limite_profundidade, profundidade_atual + 1,
                             folhas, filhos, heuristica)
            for c in filhos[no]]
    return max(valores) if eh_max else min(valores)


def minimax_limitado_rastreio(limite_profundidade=2, folhas=FOLHAS,
                           filhos=FILHOS, heuristica=HEURISTICA):
    # Trace do Minimax limitado.
    resultados = {}

    def _ml(no, eh_max, d):
        if d >= limite_profundidade:
            valor = heuristica.get(no, 0)
            resultados[no] = ('MAX' if eh_max else 'MIN', valor, 'heuristica')
            return valor
        if no not in filhos:
            valor = max(folhas[no]) if eh_max else min(folhas[no])
            resultados[no] = ('MAX' if eh_max else 'MIN', valor, 'folha')
            return valor
        valores = [_ml(c, not eh_max, d + 1) for c in filhos[no]]
        valor = max(valores) if eh_max else min(valores)
        resultados[no] = ('MAX' if eh_max else 'MIN', valor, 'interno')
        return valor

    valor_raiz = _ml('A', True, 0)
    return valor_raiz, resultados


# EXPERIMENTO: MODIFICACAO DE 3 FOLHAS
FOLHAS_MOD = {
    'E': [10, 5],   # era [3, 5]
    'F': [6, 1],    # era [6, 9]
    'G': [1, 2],
    'H': [0, -1],
    'I': [3, 4],    # era [7, 4]
    'J': [5, 6],
}


# IMPRESSAO DOS RESULTADOS
def sep(title=''):
    print('\n' + '=' * 60)
    if title:
        print(title)
        print('=' * 60)


def main():
    sep('PARTE 1 - MINIMAX COMPLETO')
    valor_raiz, mm_resultados = minimax_rastreio_completo()

    print(f'\nValor na raiz A: {valor_raiz}')
    print(f'Caminho escolhido por MAX: A -> D (valor {valor_raiz})\n')

    print(f"{'No':<5} {'Tipo':<6} {'Valor Minimax'}")
    print('-' * 22)
    order = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    for n in order:
        t, v = mm_resultados[n]
        print(f"{n:<5} {t:<6} {v}")

    sep('PARTE 2 - PODA ALPHA-BETA (ordem esquerda para direita)')
    ab_valor, ab_estatisticas = alpha_beta('A', True, -math.inf, math.inf,
                                  estatisticas={'nos': 0, 'podas': 0,
                                         'nos_podados': []})
    _, ab_passos = alpha_beta_rastreio_compacto()

    print(f'\nValor Alpha-Beta: {ab_valor}')
    print(f'Numero de podas: {ab_estatisticas["podas"]}')
    print(f'Nos podados: {ab_estatisticas["nos_podados"]}')
    print(f'Nos nao explorados: no H + 2 folhas = 3 nos\n')

    print(f"{'Passo':<7} {'No':<5} {'Tipo':<5} {'alfa':<10} {'beta':<10} {'Poda?'}")
    print('-' * 45)

    # Tabela compacta (cada no uma vez + folhas/podas)
    for r in ab_passos:
        print(f"{r['passo']:<7} {r['no']:<5} {r['tipo']:<5} {r['alpha']:<10} {r['beta']:<10} {r['podado']}")

    print('\nMotivo da poda em C (subarvore de H):')
    print('  C(MIN) apos ver G=2 tem beta=2. A(MAX) tem alpha=5.')
    print('  Como beta(2) <= alpha(5), H nao pode melhorar o resultado de C.')
    print('  Qualquer valor de H sera >= ao valor de C (que e MIN).')
    print('  C nunca retornara valor > 2, que e < alpha=5, entao')
    print('  A nunca escolhera C. Poda valida.')

    sep('PARTE 3 - ORDEM OTIMA DE EXPANSAO')
    print('Ordem original: A(B,C,D) | B(E,F) | C(G,H) | D(I,J)')
    print('  -> 1 poda (H podado)')
    print()
    print('Ordem otima: A(D,B,C) | D(J,I) | B(E,F) | C(H,G)')
    print('  -> 2 podas (F e G podados)')
    print()

    # Verificar com alpha_beta usando ordem otima
    filhos_otimo = {
        'A': ['D', 'B', 'C'],
        'D': ['J', 'I'],
        'B': ['E', 'F'],
        'C': ['H', 'G'],
    }
    folhas_otimo = FOLHAS
    ab_valor_otimo, ab_estatisticas_otimo = alpha_beta(
        'A', True, -math.inf, math.inf,
        folhas=folhas_otimo, filhos=filhos_otimo,
        estatisticas={'nos': 0, 'podas': 0, 'nos_podados': []})

    print(f'Valor com ordem otima: {ab_valor_otimo}')
    print(f'Podas com ordem otima: {ab_estatisticas_otimo["podas"]}')
    print(f'Nos podados: {ab_estatisticas_otimo["nos_podados"]}')
    print(f'Nos nao explorados: F(+2 folhas) + G(+2 folhas) = 6 nos')
    print()
    print('Comparativo:')
    print(f'  Ordem original -> 1 poda,  3 nos nao explorados')
    print(f'  Ordem otima    -> 2 podas, 6 nos nao explorados')

    sep('PARTE 4 - MINIMAX COM PROFUNDIDADE LIMITADA (profundidade=2)')
    lim_valor, lim_resultados = minimax_limitado_rastreio(limite_profundidade=2)

    print('\nValores heuristicos aplicados nos nos de profundidade 2:')
    for n, v in HEURISTICA.items():
        print(f'  {n}: {v}')

    print(f'\nB(MIN) = min(h(E)={HEURISTICA["E"]}, h(F)={HEURISTICA["F"]}) = {min(HEURISTICA["E"], HEURISTICA["F"])}')
    print(f'C(MIN) = min(h(G)={HEURISTICA["G"]}, h(H)={HEURISTICA["H"]}) = {min(HEURISTICA["G"], HEURISTICA["H"])}')
    print(f'D(MIN) = min(h(I)={HEURISTICA["I"]}, h(J)={HEURISTICA["J"]}) = {min(HEURISTICA["I"], HEURISTICA["J"])}')
    print(f'A(MAX) = max({min(HEURISTICA["E"],HEURISTICA["F"])}, {min(HEURISTICA["G"],HEURISTICA["H"])}, {min(HEURISTICA["I"],HEURISTICA["J"])}) = {lim_valor}')

    print(f'\nMinimax completo : A={valor_raiz}, decisao -> D')
    print(f'Minimax limitado : A={lim_valor}, decisao -> B')
    print('Conclusao: as decisoes DIFEREM.')

    sep('PARTE 5 - COMPARACAO MINIMAX vs ALPHA-BETA')
    # Contagem de nos Minimax: todos os nos internos + todas as folhas
    mm_nos = len(order)  # 10 nos visitados
    mm_chamadas_folha = 12     # 12 valores terminais avaliados

    # Contagem Alpha-Beta (ordem original): H nao visitado
    ab_nos_visitados = mm_nos - 1    # H nao visitado
    ab_chamadas_folha = mm_chamadas_folha - 2  # 2 folhas de H nao avaliadas

    print(f'\n{"Campo de analise":<35} {"Minimax":<15} {"Alpha-Beta"}')
    print('-' * 65)
    fields = [
        ('Nos internos explorados',          str(mm_nos),         str(ab_nos_visitados)),
        ('Valores terminais avaliados',       str(mm_chamadas_folha),    str(ab_chamadas_folha)),
        ('Total de avaliacoes',               str(mm_nos+mm_chamadas_folha), str(ab_nos_visitados+ab_chamadas_folha)),
        ('Numero de podas',                   '0',                   '1'),
        ('Nos nao explorados',                '0',                   '3 (H + 2 folhas)'),
        ('Custo computacional (O)',           'O(b^m)',              'O(b^(m/2)) melhor caso'),
        ('Consumo de memoria',                'O(bm)',               'O(bm)'),
        ('Impacto da ordenacao',              'Nenhum',              'Alto (mais podas)'),
        ('Qualidade da decisao',              'Otima (6, -> D)',     'Otima (6, -> D)'),
    ]
    for f in fields:
        print(f'{f[0]:<35} {f[1]:<15} {f[2]}')

    sep('PARTE 6 - MODIFICACAO DE 3 FOLHAS')
    print('Modificacoes aplicadas:')
    print('  E: [3, 5] -> [10, 5]')
    print('  F: [6, 9] -> [6,  1]')
    print('  I: [7, 4] -> [3,  4]')

    raiz_mod, mm_modificado = minimax_rastreio_completo(folhas=FOLHAS_MOD)
    ab_modificado, ab_estatisticas_modificado = alpha_beta(
        'A', True, -math.inf, math.inf,
        folhas=FOLHAS_MOD,
        estatisticas={'nos': 0, 'podas': 0, 'nos_podados': []})

    print(f'\nMinimax original : A={valor_raiz}, decisao -> D')
    print(f'Minimax modificado: A={raiz_mod}, decisao -> B')
    print(f'Alpha-Beta original  : A={ab_valor}, podas=1')
    print(f'Alpha-Beta modificado: A={ab_modificado}, podas={ab_estatisticas_modificado["podas"]}')
    print(f'Nos podados (mod): {ab_estatisticas_modificado["nos_podados"]}')
    print('\nTabela comparativa:')
    print(f"{'No':<5} {'Tipo':<6} {'Valor original':<16} {'Valor modificado'}")
    print('-' * 38)
    for n in order:
        t_orig, v_orig = mm_resultados[n]
        t_mod, v_mod = mm_modificado[n]
        mark = ' <--' if v_orig != v_mod else ''
        print(f"{n:<5} {t_orig:<6} {str(v_orig):<16} {v_mod}{mark}")

    print('\nConclusao:')
    print('  O valor final de A permaneceu 6, mas a DECISAO mudou (D -> B).')
    print('  Isso demonstra sensibilidade da escolha do caminho')
    print('  mesmo quando o valor otimo se mantem.')
    print('  Alpha-Beta agora realiza 2 podas (H e J).')


if __name__ == '__main__':
    main()