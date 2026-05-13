import time
import tracemalloc
from copy import deepcopy


# DEFINIÇÃO DO PROBLEMA CSP
TURNOS = ['T1', 'T2', 'T3', 'T4', 'T5', 'T6']
MEDICOS = ['A', 'B', 'C', 'D']

def obtem_dominios_iniciais():
    dominios = {}
    for t in TURNOS:
        dominios[t] = list(MEDICOS)
    # Restrição unária: A não pode trabalhar em T3
    dominios['T3'] = [d for d in MEDICOS if d != 'A']
    return dominios

def verifica_consistente(atribuicao, variavel, valor):
    # Verifica todas as restrições para uma atribuição.
    indice = TURNOS.index(variavel)
    
    # Restrição 1: sem turnos consecutivos
    if indice > 0:
        ant = TURNOS[indice - 1]
        if ant in atribuicao and atribuicao[ant] == valor:
            return False
    if indice < len(TURNOS) - 1:
        prox = TURNOS[indice + 1]
        if prox in atribuicao and atribuicao[prox] == valor:
            return False
    
    # Restrição unária: A não pode trabalhar em T3
    if variavel == 'T3' and valor == 'A':
        return False
    
    return True

def verifica_consistente_completo(atribuicao):
    # Verifica restrições globais em uma atribuição completa.
    # B deve trabalhar em pelo menos um turno entre T1, T2
    b_em_t1t2 = any(atribuicao.get(t) == 'B' for t in ['T1', 'T2'])
    if not b_em_t1t2:
        return False
    
    # C não pode trabalhar simultaneamente em T2 e T5
    if atribuicao.get('T2') == 'C' and atribuicao.get('T5') == 'C':
        return False
    
    # D pode trabalhar no máximo dois turnos
    contagem_d = sum(1 for t in TURNOS if atribuicao.get(t) == 'D')
    if contagem_d > 2:
        return False
    
    return True

def verifica_restricoes_globais_parcial(atribuicao):
    # Verifica restrições globais para atribuição parcial (poda antecipada).
    # D pode trabalhar no máximo dois turnos
    contagem_d = sum(1 for t in TURNOS if atribuicao.get(t) == 'D')
    if contagem_d > 2:
        return False
    
    # C não pode trabalhar simultaneamente em T2 e T5
    if atribuicao.get('T2') == 'C' and atribuicao.get('T5') == 'C':
        return False
    
    return True

# BACKTRACKING SIMPLES
bt_estados = 0
bt_retrocessos = 0
bt_passos = []

def backtracking(atribuicao, dominios):
    global bt_estados, bt_retrocessos
    
    if len(atribuicao) == len(TURNOS):
        if verifica_consistente_completo(atribuicao):
            return atribuicao
        return None
    
    # Próxima variável não atribuída (ordem fixa)
    variavel = next(t for t in TURNOS if t not in atribuicao)
    
    for valor in dominios[variavel]:
        bt_estados += 1
        if verifica_consistente(atribuicao, variavel, valor):
            atribuicao[variavel] = valor
            if verifica_restricoes_globais_parcial(atribuicao):
                resultado = backtracking(atribuicao, dominios)
                if resultado:
                    return resultado
            bt_retrocessos += 1
            del atribuicao[variavel]
    
    return None

# BACKTRACKING + MRV
mrv_estados = 0
mrv_retrocessos = 0

def seleciona_mrv(atribuicao, dominios):
    # Seleciona variável com menor número de valores restantes.
    nao_atribuidos = [t for t in TURNOS if t not in atribuicao]
    return min(nao_atribuidos, key=lambda variavel: len(dominios[variavel]))

def backtracking_mrv(atribuicao, dominios):
    global mrv_estados, mrv_retrocessos
    
    if len(atribuicao) == len(TURNOS):
        if verifica_consistente_completo(atribuicao):
            return atribuicao
        return None
    
    variavel = seleciona_mrv(atribuicao, dominios)
    
    for valor in dominios[variavel]:
        mrv_estados += 1
        if verifica_consistente(atribuicao, variavel, valor):
            atribuicao[variavel] = valor
            if verifica_restricoes_globais_parcial(atribuicao):
                resultado = backtracking_mrv(atribuicao, dominios)
                if resultado:
                    return resultado
            mrv_retrocessos += 1
            del atribuicao[variavel]
    
    return None

# BACKTRACKING + MRV + DEGREE HEURISTIC
mrv_deg_estados = 0
mrv_deg_retrocessos = 0

def conta_restricoes(variavel, atribuicao, dominios):
    # Conta restrições com variáveis não atribuídas (degree).
    indice = TURNOS.index(variavel)
    contagem = 0
    nao_atribuidos = [t for t in TURNOS if t not in atribuicao and t != variavel]
    for u in nao_atribuidos:
        u_indice = TURNOS.index(u)
        if abs(indice - u_indice) == 1:  # adjacente
            contagem += 1
    return contagem

def seleciona_mrv_grau(atribuicao, dominios):
    # MRV com desempate por degree heuristic.
    nao_atribuidos = [t for t in TURNOS if t not in atribuicao]
    min_restante = min(len(dominios[variavel]) for variavel in nao_atribuidos)
    candidatos = [variavel for variavel in nao_atribuidos if len(dominios[variavel]) == min_restante]
    # Desempate: maior degree (mais restrições com vizinhos não atribuídos)
    return max(candidatos, key=lambda variavel: conta_restricoes(variavel, atribuicao, dominios))

def backtracking_mrv_grau(atribuicao, dominios):
    global mrv_deg_estados, mrv_deg_retrocessos
    
    if len(atribuicao) == len(TURNOS):
        if verifica_consistente_completo(atribuicao):
            return atribuicao
        return None
    
    variavel = seleciona_mrv_grau(atribuicao, dominios)
    
    for valor in dominios[variavel]:
        mrv_deg_estados += 1
        if verifica_consistente(atribuicao, variavel, valor):
            atribuicao[variavel] = valor
            if verifica_restricoes_globais_parcial(atribuicao):
                resultado = backtracking_mrv_grau(atribuicao, dominios)
                if resultado:
                    return resultado
            mrv_deg_retrocessos += 1
            del atribuicao[variavel]
    
    return None

# FORWARD CHECKING
fc_estados = 0
fc_retrocessos = 0
fc_reducoes_dominio = []

def checa_adiante(variavel, valor, atribuicao, dominios):
    # Propaga restrições para variáveis não atribuídas.
    podado = {}
    indice = TURNOS.index(variavel)
    
    # Restrição de não-consecutividade
    vizinhos = []
    if indice > 0:
        vizinhos.append(TURNOS[indice - 1])
    if indice < len(TURNOS) - 1:
        vizinhos.append(TURNOS[indice + 1])
    
    for vizinho in vizinhos:
        if vizinho not in atribuicao:
            if valor in dominios[vizinho]:
                if vizinho not in podado:
                    podado[vizinho] = []
                podado[vizinho].append(valor)
                dominios[vizinho].remove(valor)
                if not dominios[vizinho]:
                    return None, podado  # domínio vazio = inconsistência
    
    return dominios, podado

def backtracking_fc(atribuicao, dominios):
    global fc_estados, fc_retrocessos
    
    if len(atribuicao) == len(TURNOS):
        if verifica_consistente_completo(atribuicao):
            return atribuicao
        return None
    
    variavel = seleciona_mrv(atribuicao, dominios)
    
    for valor in list(dominios[variavel]):
        fc_estados += 1
        if verifica_consistente(atribuicao, variavel, valor):
            atribuicao[variavel] = valor
            copia_dominios = deepcopy(dominios)
            resultado_dominios, podado = checa_adiante(variavel, valor, atribuicao, dominios)
            
            if resultado_dominios is not None and verifica_restricoes_globais_parcial(atribuicao):
                resultado = backtracking_fc(atribuicao, dominios)
                if resultado:
                    return resultado
            
            fc_retrocessos += 1
            del atribuicao[variavel]
            # Restaurar domínios podados
            for vizinho, valores in podado.items():
                for v in valores:
                    if v not in dominios[vizinho]:
                        dominios[vizinho].append(v)
    
    return None

# BACKJUMPING
bj_estados = 0
bj_saltos = 0

class ExcecaoBackjump(Exception):
    def __init__(self, conjunto_conflito):
        self.conjunto_conflito = conjunto_conflito

def backtracking_bj_aux(atribuicao, indice_ordem, conjuntos_conflito):
    global bj_estados, bj_saltos
    
    if indice_ordem == len(TURNOS):
        if verifica_consistente_completo(atribuicao):
            return atribuicao
        return None
    
    variavel = TURNOS[indice_ordem]
    dominios = obtem_dominios_iniciais()
    
    conflito_local = set()
    
    for valor in dominios[variavel]:
        bj_estados += 1
        if verifica_consistente(atribuicao, variavel, valor):
            atribuicao[variavel] = valor
            if verifica_restricoes_globais_parcial(atribuicao):
                try:
                    resultado = backtracking_bj_aux(atribuicao, indice_ordem + 1, conjuntos_conflito)
                    if resultado:
                        return resultado
                except ExcecaoBackjump as e:
                    if variavel in e.conjunto_conflito:
                        conflito_local |= (e.conjunto_conflito - {variavel})
                        del atribuicao[variavel]
                        continue
                    else:
                        del atribuicao[variavel]
                        raise
            del atribuicao[variavel]
        else:
            # Registrar conflito
            indice = TURNOS.index(variavel)
            if indice > 0:
                ant = TURNOS[indice - 1]
                if ant in atribuicao and atribuicao[ant] == valor:
                    conflito_local.add(ant)
    
    if conflito_local:
        bj_saltos += 1
        raise ExcecaoBackjump(conflito_local | {variavel})
    
    return None

def backtracking_backjump(atribuicao, dominios):
    try:
        return backtracking_bj_aux(atribuicao, 0, {})
    except ExcecaoBackjump:
        return None

# EXECUÇÃO E COLETA DE RESULTADOS

print("=" * 70)
print("CSP - ESCALA DE PLANTÕES HOSPITALARES")
print("=" * 70)

resultados = {}

algoritmos = [
    ("Backtracking Simples", backtracking, False),
    ("Backtracking + MRV", backtracking_mrv, False),
    ("Backtracking + MRV + Degree", backtracking_mrv_grau, False),
    ("Forward Checking", backtracking_fc, False),
    ("Backjumping", backtracking_backjump, False),
]

for nome, algo, _ in algoritmos:
    bt_estados = mrv_estados = mrv_deg_estados = fc_estados = bj_estados = 0
    bt_retrocessos = mrv_retrocessos = mrv_deg_retrocessos = fc_retrocessos = bj_saltos = 0
    
    dominios = obtem_dominios_iniciais()
    atribuicao = {}
    
    tracemalloc.start()
    t0 = time.perf_counter()
    solucao = algo(atribuicao, dominios)
    t1 = time.perf_counter()
    atual, pico = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    if nome == "Backtracking Simples":
        estados = bt_estados; retrocessos = bt_retrocessos
    elif nome == "Backtracking + MRV":
        estados = mrv_estados; retrocessos = mrv_retrocessos
    elif nome == "Backtracking + MRV + Degree":
        estados = mrv_deg_estados; retrocessos = mrv_deg_retrocessos
    elif nome == "Forward Checking":
        estados = fc_estados; retrocessos = fc_retrocessos
    else:
        estados = bj_estados; retrocessos = bj_saltos
    
    resultados[nome] = {
        'solution': solucao,
        'estados': estados,
        'backtracks': retrocessos,
        'time_ms': (t1 - t0) * 1000,
        'memory_kb': pico / 1024,
    }
    
    print(f"\n{'='*50}")
    print(f"Algoritmo: {nome}")
    print(f"Solução: {solucao}")
    print(f"Estados explorados: {estados}")
    print(f"Retrocessos: {retrocessos}")
    print(f"Tempo: {(t1-t0)*1000:.4f} ms")
    print(f"Memória pico: {pico/1024:.2f} KB")

# TRACE DO BACKTRACKING SIMPLES (para tabela passo a passo)
print("\n" + "="*70)
print("TRACE DETALHADO DO BACKTRACKING SIMPLES")
print("="*70)

passos_trace = []
contador_passo = [0]

def backtracking_trace(atribuicao, dominios):
    if len(atribuicao) == len(TURNOS):
        if verifica_consistente_completo(atribuicao):
            return atribuicao
        return None
    
    variavel = next(t for t in TURNOS if t not in atribuicao)
    
    for valor in dominios[variavel]:
        contador_passo[0] += 1
        copia_estado = dict(atribuicao)
        copia_estado[variavel] = valor
        
        if verifica_consistente(atribuicao, variavel, valor):
            atribuicao[variavel] = valor
            if verifica_restricoes_globais_parcial(atribuicao):
                passos_trace.append({
                    'step': contador_passo[0],
                    'variavel': variavel,
                    'valor': valor,
                    'status': 'OK',
                    'state': dict(atribuicao)
                })
                resultado = backtracking_trace(atribuicao, dominios)
                if resultado:
                    return resultado
                passos_trace.append({
                    'step': contador_passo[0],
                    'variavel': variavel,
                    'valor': valor,
                    'status': 'BACKTRACK',
                    'state': dict(atribuicao)
                })
                contador_passo[0] += 1
            else:
                passos_trace.append({
                    'step': contador_passo[0],
                    'variavel': variavel,
                    'valor': valor,
                    'status': 'GLOBAL_CONFLICT',
                    'state': copia_estado
                })
            del atribuicao[variavel]
        else:
            passos_trace.append({
                'step': contador_passo[0],
                'variavel': variavel,
                'valor': valor,
                'status': 'CONFLICT',
                'state': copia_estado
            })
    
    return None

backtracking_trace({}, obtem_dominios_iniciais())

print(f"\n{'Passo':<6} {'Variável':<12} {'Status':<18} Estado Parcial")
print("-"*80)
mostrados = []
for s in passos_trace[:40]:  # Mostrar primeiros 40 passos
    str_estado = "{" + ", ".join(f"{k}={v}" for k,v in s['state'].items()) + "}"
    print(f"{s['step']:<6} {s['variavel']+'='+s['valor']:<12} {s['status']:<18} {str_estado}")

# TRACE DO FORWARD CHECKING (domínios após atribuição)
print("\n" + "="*70)
print("TRACE FORWARD CHECKING - Reduções de Domínio")
print("="*70)

trace_fc = []

def backtracking_fc_trace(atribuicao, dominios, profundidade=0):
    if len(atribuicao) == len(TURNOS):
        if verifica_consistente_completo(atribuicao):
            return atribuicao
        return None
    
    variavel = seleciona_mrv(atribuicao, dominios)
    
    for valor in list(dominios[variavel]):
        if verifica_consistente(atribuicao, variavel, valor):
            atribuicao[variavel] = valor
            dominios_antes = {k: list(v) for k, v in dominios.items()}
            resultado_dominios, podado = checa_adiante(variavel, valor, atribuicao, dominios)
            
            trace_fc.append({
                'atribuicao': dict(atribuicao),
                'podado': podado,
                'domains_after': {k: list(v) for k, v in dominios.items()},
                'inconsistent': resultado_dominios is None
            })
            
            if resultado_dominios is not None and verifica_restricoes_globais_parcial(atribuicao):
                resultado = backtracking_fc_trace(atribuicao, dominios, profundidade+1)
                if resultado:
                    return resultado
            
            del atribuicao[variavel]
            for vizinho, valores in podado.items():
                for v in valores:
                    if v not in dominios[vizinho]:
                        dominios[vizinho].append(v)
    
    return None

backtracking_fc_trace({}, obtem_dominios_iniciais())

print(f"\nPrimeiras atribuições com forward checking:")
for i, entrada in enumerate(trace_fc[:10]):
    str_atribuicao = ", ".join(f"{k}={v}" for k,v in entrada['atribuicao'].items())
    str_podado = str(entrada['podado']) if entrada['podado'] else "{}"
    inc = " [INCONSISTENTE]" if entrada['inconsistent'] else ""
    print(f"  [{i+1}] {{{str_atribuicao}}}")
    print(f"       Podas: {str_podado}{inc}")

print("\n" + "="*70)
print("TABELA RESUMO DOS ALGORITMOS")
print("="*70)
print(f"\n{'Algoritmo':<30} {'Estados':>10} {'Retrocessos':>12} {'Tempo(ms)':>12} {'Mem(KB)':>10}")
print("-"*78)
for nome, dados in resultados.items():
    print(f"{nome:<30} {dados['estados']:>10} {dados['backtracks']:>12} {dados['time_ms']:>12.4f} {dados['memory_kb']:>10.2f}")