import math
import random
import copy

# ─────────────────────────────────────────────
#  BOARD REPRESENTATION
#  4x4 grid, row 0 = top, row 3 = bottom
#  1 = RED (V), 2 = YELLOW (A), 0 = empty
# ─────────────────────────────────────────────
ROWS = 4
COLS = 4
RED = 1
YELLOW = 2

def make_initial_board():
    board = [[0]*COLS for _ in range(ROWS)]
    # V at [3,0] and [2,1]; A at [2,0] and [3,1]
    board[3][0] = RED
    board[2][1] = RED
    board[2][0] = YELLOW
    board[3][1] = YELLOW
    return board

def drop_piece(board, col, player):
    b = copy.deepcopy(board)
    for row in range(ROWS-1, -1, -1):
        if b[row][col] == 0:
            b[row][col] = player
            return b, row
    return None, -1  # column full

def is_valid_col(board, col):
    return board[0][col] == 0

def get_valid_cols(board):
    return [c for c in range(COLS) if is_valid_col(board, c)]

def check_winner(board):
    # horizontal
    for r in range(ROWS):
        for c in range(COLS-3):
            p = board[r][c]
            if p != 0 and all(board[r][c+i] == p for i in range(4)):
                return p
    # vertical
    for r in range(ROWS-3):
        for c in range(COLS):
            p = board[r][c]
            if p != 0 and all(board[r+i][c] == p for i in range(4)):
                return p
    # diagonal \
    for r in range(ROWS-3):
        for c in range(COLS-3):
            p = board[r][c]
            if p != 0 and all(board[r+i][c+i] == p for i in range(4)):
                return p
    # diagonal /
    for r in range(3, ROWS):
        for c in range(COLS-3):
            p = board[r][c]
            if p != 0 and all(board[r-i][c+i] == p for i in range(4)):
                return p
    return 0

def is_terminal(board):
    return check_winner(board) != 0 or len(get_valid_cols(board)) == 0

def print_board(board):
    for row in board:
        print(' '.join(['.','V','A'][c] for c in row))
    print()

# ─────────────────────────────────────────────
#  ROLLOUT POLICIES
# ─────────────────────────────────────────────
def rollout_random(board, player):
    b = copy.deepcopy(board)
    cur = player
    while not is_terminal(b):
        cols = get_valid_cols(b)
        col = random.choice(cols)
        b, _ = drop_piece(b, col, cur)
        cur = YELLOW if cur == RED else RED
    w = check_winner(b)
    if w == RED: return 1
    if w == YELLOW: return -1
    return 0

def rollout_semi_greedy(board, player):
    b = copy.deepcopy(board)
    cur = player
    center_priority = [1, 3, 0, 2]  # prefer cols 1,3 then 0,2 (1-indexed: c2,c4,c1,c3)
    while not is_terminal(b):
        cols = get_valid_cols(b)
        # 1. Check if current player can win immediately
        for c in cols:
            nb, _ = drop_piece(b, c, cur)
            if nb and check_winner(nb) == cur:
                b = nb
                cur = YELLOW if cur == RED else RED
                break
        else:
            # 2. Block opponent immediate win
            opp = YELLOW if cur == RED else RED
            blocked = False
            for c in cols:
                nb, _ = drop_piece(b, c, opp)
                if nb and check_winner(nb) == opp:
                    b, _ = drop_piece(b, c, cur)
                    cur = YELLOW if cur == RED else RED
                    blocked = True
                    break
            if not blocked:
                # 3. Prefer central columns
                for c in center_priority:
                    if c in cols:
                        b, _ = drop_piece(b, c, cur)
                        cur = YELLOW if cur == RED else RED
                        break
    w = check_winner(b)
    if w == RED: return 1
    if w == YELLOW: return -1
    return 0

# ─────────────────────────────────────────────
#  MCTS NODE
# ─────────────────────────────────────────────
class MCTSNode:
    def __init__(self, board, player, parent=None, move=None):
        self.board = board
        self.player = player      # player whose turn it is
        self.parent = parent
        self.move = move          # column that led here
        self.children = []
        self.N = 0                # visits
        self.W = 0                # wins (from RED perspective)
        self.untried = get_valid_cols(board)
        random.shuffle(self.untried)

    def is_fully_expanded(self):
        return len(self.untried) == 0

    def best_child(self, C):
        return max(self.children,
                   key=lambda c: (c.W/c.N) + C*math.sqrt(math.log(self.N)/c.N))

    def uct_values(self, C):
        vals = {}
        for ch in self.children:
            exploit = ch.W / ch.N
            explore = C * math.sqrt(math.log(self.N) / ch.N)
            vals[ch.move] = (exploit + explore, exploit, explore)
        return vals

# ─────────────────────────────────────────────
#  MCTS ALGORITHM
# ─────────────────────────────────────────────
def mcts(root_board, root_player, n_iter, C=1.4, rollout_fn=rollout_random, verbose=False):
    root = MCTSNode(root_board, root_player)

    iteration_log = []

    for it in range(1, n_iter+1):
        # ── SELECTION ──
        node = root
        path = []
        while node.is_fully_expanded() and node.children and not is_terminal(node.board):
            node = node.best_child(C)
            path.append(node.move)

        # ── EXPANSION ──
        expanded_move = None
        if not is_terminal(node.board) and node.untried:
            col = node.untried.pop()
            new_board, _ = drop_piece(node.board, col, node.player)
            next_player = YELLOW if node.player == RED else RED
            child = MCTSNode(new_board, next_player, parent=node, move=col)
            node.children.append(child)
            node = child
            expanded_move = col
            path.append(col)

        # ── ROLLOUT ──
        result = rollout_fn(node.board, node.player)

        # ── BACKPROP ──
        n = node
        while n is not None:
            n.N += 1
            # W counts wins for RED
            if result == 1:
                n.W += 1
            n = n.parent

        if verbose:
            # snapshot root children stats
            stats = {ch.move: (ch.N, ch.W) for ch in root.children}
            uct = root.uct_values(C)
            iteration_log.append({
                'iter': it,
                'path': list(path),
                'expanded': expanded_move,
                'result': result,
                'stats': copy.deepcopy(stats),
                'uct': copy.deepcopy(uct),
            })

    return root, iteration_log

# ─────────────────────────────────────────────
#  DETERMINISTIC SEED FOR REPRODUCIBILITY
# ─────────────────────────────────────────────
random.seed(42)

INIT_BOARD = make_initial_board()
print("=== Initial Board ===")
print_board(INIT_BOARD)

# ─────────────────────────────────────────────
#  10 ITERATIONS VERBOSE (C=1.4, random rollout)
# ─────────────────────────────────────────────
random.seed(42)
root14, log14 = mcts(INIT_BOARD, RED, 10, C=1.4, rollout_fn=rollout_random, verbose=True)

print("=== 10 Iterations (C=1.4, Random Rollout) ===")
for entry in log14:
    it = entry['iter']
    path_str = ' -> '.join([f'c{c+1}' for c in entry['path']]) if entry['path'] else 'root'
    exp_str = f"c{entry['expanded']+1}" if entry['expanded'] is not None else 'none'
    res_str = {1:'RED wins', -1:'YELLOW wins', 0:'draw'}[entry['result']]
    print(f"\nIteration {it}:")
    print(f"  Path selected: {path_str}")
    print(f"  Expanded node: {exp_str}")
    print(f"  Rollout result: {res_str}")
    print(f"  Root children stats (N, W):")
    for col in sorted(entry['stats'].keys()):
        n, w = entry['stats'][col]
        print(f"    c{col+1}: N={n}, W={w}", end='')
        if col in entry['uct']:
            uct_val, exploit, explore = entry['uct'][col]
            print(f"  UCT={uct_val:.4f} (exploit={exploit:.4f}, explore={explore:.4f})", end='')
        print()

# Final table
print("\n=== Final Table (C=1.4) ===")
print(f"{'Jogada':<8} {'Visitas':>8} {'Vitorias':>10} {'UCT':>10}")
for ch in sorted(root14.children, key=lambda x: x.move):
    N = root14.N
    if ch.N > 0:
        exploit = ch.W / ch.N
        explore = 1.4 * math.sqrt(math.log(N) / ch.N)
        uct = exploit + explore
    else:
        uct = float('inf')
    print(f"c{ch.move+1:<7} {ch.N:>8} {ch.W:>10} {uct:>10.4f}")

# ─────────────────────────────────────────────
#  COMPARE C VALUES  (200 iterations each)
# ─────────────────────────────────────────────
print("\n=== C Value Comparison (200 iterations, random rollout) ===")
results_C = {}
for C_val in [0.1, 1.4, 3.0]:
    random.seed(42)
    root_c, _ = mcts(INIT_BOARD, RED, 200, C=C_val, rollout_fn=rollout_random, verbose=False)
    col_visits = {ch.move: (ch.N, ch.W) for ch in root_c.children}
    best = max(root_c.children, key=lambda x: x.N).move
    results_C[C_val] = {'visits': col_visits, 'best': best, 'root_N': root_c.N}
    print(f"\nC={C_val}:")
    print(f"  Best move: c{best+1}")
    total_children = sum(ch.N for ch in root_c.children)
    for col in sorted(col_visits.keys()):
        n, w = col_visits[col]
        print(f"  c{col+1}: N={n}, W={w}, frac={n/total_children:.3f}")

# ─────────────────────────────────────────────
#  COMPARE ROLLOUT TYPES (200 iterations, C=1.4)
# ─────────────────────────────────────────────
print("\n=== Rollout Comparison (200 iterations, C=1.4) ===")
for label, fn in [('Random', rollout_random), ('Semi-Greedy', rollout_semi_greedy)]:
    random.seed(42)
    root_r, _ = mcts(INIT_BOARD, RED, 200, C=1.4, rollout_fn=fn, verbose=False)
    best = max(root_r.children, key=lambda x: x.N).move
    print(f"\n{label}:")
    print(f"  Best move: c{best+1}")
    for ch in sorted(root_r.children, key=lambda x: x.move):
        wr = ch.W/ch.N if ch.N > 0 else 0
        print(f"  c{ch.move+1}: N={ch.N}, W={ch.W}, WR={wr:.3f}")

# ─────────────────────────────────────────────
#  CONVERGENCE: iterations needed to stabilize
# ─────────────────────────────────────────────
print("\n=== Convergence Analysis ===")
for label, fn in [('Random', rollout_random), ('Semi-Greedy', rollout_semi_greedy)]:
    prev_best = None
    stable_at = None
    for n_it in [10, 25, 50, 100, 200, 500]:
        random.seed(42)
        root_conv, _ = mcts(INIT_BOARD, RED, n_it, C=1.4, rollout_fn=fn, verbose=False)
        best = max(root_conv.children, key=lambda x: x.N).move
        print(f"  {label} | iter={n_it:4d} | best=c{best+1}")