"""pick_u.py: random outer-step triples U = (y, Y9, w8) for the brute-force comparison: the first NWANT with at
least one solution of the PARTIAL system (dg1, de2) for the NT heaviest targets, plus NZERO with none but a large
search tree.  Writes brute_cases.txt (one case per line: y Y9 w8 nsol nodes) and the e3dfs solution lists."""
import sys, random
sys.dont_write_bytecode = True
import e3dfs as D

NT, NWANT, NZERO, seed = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
rows, _ = D.load_targets(NT)
targets = [D.outcome_target(r[2], r[3]) for r in rows]
rng = random.Random(seed)
pos, zero = [], []
tries = 0
while len(pos) < NWANT or len(zero) < NZERO:
    tries += 1
    y, Y9, w8 = D.rand_member(rng), rng.getrandbits(32), rng.getrandbits(32)
    sols, nodes = D.search(y, Y9, w8, targets, partial=True)
    n = sum(nodes)
    if sols and len(pos) < NWANT:
        pos.append((y, Y9, w8, sorted(sols), n))
    elif not sols and n > 3000 and len(zero) < NZERO:
        zero.append((y, Y9, w8, [], n))
with open('brute_cases.txt', 'w') as f:
    f.write(f'# NT {NT} tries {tries}\n')
    for y, Y9, w8, s, n in pos + zero:
        f.write(f'{y:08x} {Y9:08x} {w8:08x} {len(s)} {n} ' + ','.join(f'{h:08x}:{ti}' for h, ti in s) + '\n')
tg = ' '.join(f'{t[0]:08x}:{t[1]:08x}' for t in targets)
with open('brute_targets.txt', 'w') as f:
    f.write(tg + '\n')
print(f'tries {tries}; with solutions {len(pos)}, zero-with-large-tree {len(zero)}')
