import re

with open("q5.py", "r") as f:
    text = f.read()

replacements = {
    r'\bLEAVES\b': 'FOLHAS',
    r'\bCHILDREN\b': 'FILHOS',
    r'\bHEURISTIC\b': 'HEURISTICA',
    r'\bLEAVES_MOD\b': 'FOLHAS_MOD',
    r'\bis_max\b': 'eh_max',
    r'\bnode\b': 'no',
    r'\bleaves\b': 'folhas',
    r'\bchildren\b': 'filhos',
    r'\bval\b': 'valor',
    r'\bvalues\b': 'valores',
    r'\bvals\b': 'valores',
    r'\bchild\b': 'filho',
    r'\bchild_val\b': 'valor_filho',
    r'\bremaining\b': 'restantes',
    r'\brem\b': 'rest',
    r'\bstats\b': 'estatisticas',
    r'\bdepth\b': 'profundidade',
    r'\bnodes\b': 'nos',
    r'\bprunings\b': 'podas',
    r'\bpruned_nodes\b': 'nos_podados',
    r'\bstep\b': 'passo',
    r'\bsteps\b': 'passos',
    r'\btype\b': 'tipo',
    r'\bpruned\b': 'podado',
    r'\bminimax_full_trace\b': 'minimax_rastreio_completo',
    r'\balpha_beta_step_trace\b': 'alpha_beta_rastreio_passo',
    r'\balpha_beta_compact_trace\b': 'alpha_beta_rastreio_compacto',
    r'\bminimax_limited\b': 'minimax_limitado',
    r'\bminimax_limited_trace\b': 'minimax_limitado_rastreio',
    r'\bdepth_limit\b': 'limite_profundidade',
    r'\bcurrent_depth\b': 'profundidade_atual',
    r'\bheuristic\b': 'heuristica',
    r'\bresults\b': 'resultados',
    r'\broot_val\b': 'valor_raiz',
    r'\balpha_str\b': 'alfa_str',
    r'\bbeta_str\b': 'beta_str',
    r'\bleaf_labels\b': 'rotulos_folha',
    r'\bnext_leaf_idx\b': 'proximo_idx_folha',
    r'\bletters\b': 'letras',
    r'\b_assign_labels\b': '_atribuir_rotulos',
    r'\b_add_row\b': '_adicionar_linha',
    r'\b_add_pruned_subtree\b': '_adicionar_subarvore_podada',
    r'\b_eval_leaf_values\b': '_avaliar_valores_folha',
    r'\bchildren_opt\b': 'filhos_otimo',
    r'\bleaves_opt\b': 'folhas_otimo',
    r'\bab_val_opt\b': 'ab_valor_otimo',
    r'\bab_stats_opt\b': 'ab_estatisticas_otimo',
    r'\bab_val\b': 'ab_valor',
    r'\bab_stats\b': 'ab_estatisticas',
    r'\bmm_results\b': 'mm_resultados',
    r'\bab_steps\b': 'ab_passos',
    r'\blim_val\b': 'lim_valor',
    r'\blim_results\b': 'lim_resultados',
    r'\bmm_nodes\b': 'mm_nos',
    r'\bmm_leaf_calls\b': 'mm_chamadas_folha',
    r'\bab_nodes_visited\b': 'ab_nos_visitados',
    r'\bab_leaf_calls\b': 'ab_chamadas_folha',
    r'\broot_mod\b': 'raiz_mod',
    r'\bmm_mod\b': 'mm_modificado',
    r'\bab_mod\b': 'ab_modificado',
    r'\bab_stats_mod\b': 'ab_estatisticas_modificado'
}

for k, v in replacements.items():
    text = re.sub(k, v, text)

with open("q5.py", "w") as f:
    f.write(text)

print("done")
