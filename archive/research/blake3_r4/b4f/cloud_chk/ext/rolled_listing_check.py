"""External check (not shipped): the rolled packed recovery circuit of bsrho.py. (1) the flat listing (with its loop control) in an interpreter vs the compiled blocks vs the
scalar compression, for the program's q and for random q words, on random inputs and on all-ones inputs (largest sums, guard bits); (2) instruction and operation counts.
usage: rolled_listing_check.py <experiments dir>"""
import sys, random
sys.dont_write_bytecode = True
sys.path.insert(0, sys.argv[1]); import bsrho as b
M32 = b.M32
def run_rolled(flat, words):
    R, pc, cnt, flag, top = [0] * 35, 0, 0, False, 0
    R[24:32] = words
    jend = max(i for i, c in enumerate(flat) if c[0] == "J")
    while pc < len(flat):
        o, d, a, c = flat[pc]; pc += 1
        if o == "I": cnt, top = b.ROUNDS, pc
        elif o == "D": cnt -= 1
        elif o == "C": flag = cnt == 0
        elif o == "Z": pc = jend + 1 if flag else pc
        elif o == "J": pc = top
        elif o == "l": R[d] = a
        else:
            R[d] = {"+": lambda: R[a] + R[c], "^": lambda: R[a] ^ R[c], "|": lambda: R[a] | R[c], "a": lambda: R[a] & c, "x": lambda: R[a] ^ c,
                    "&>": lambda: R[a] >> c, "&<": lambda: R[a] << c, "=": lambda: R[a]}[o]()
    return tuple(R[:8])
rnd = random.Random(1017)
st = b.step256()
bad = tot = 0
qws = [list(st.qwords)] + [[rnd.getrandbits(32) for _ in range(8)] for _ in range(6)] + [[M32] * 8, [0] * 8]
for qw in qws:
    fn, ops, instr = b.packed_circuit(qw)
    qint = sum(w << (32 * i) for i, w in enumerate(qw))
    for it in range(60):
        xs = [rnd.getrandbits(256) for _ in range(7)]
        if it % 5 == 1: xs = [(1 << 256) - 1] * 7
        if it % 5 == 2: xs = [(1 << 256) - 1 - rnd.getrandbits(12) for _ in range(7)]
        if it % 5 == 3: xs = [0] * 7
        got = b.packed_f(xs, 256, qw)
        want = [b.f_scalar(x, 256) ^ qint for x in xs]
        words = [sum(((x >> (32 * i)) & M32) << (b.PITCH * l) for l, x in enumerate(xs)) for i in range(8)]
        tot += 1
        bad += (got != want) + (run_rolled(fn.flat, words) != fn(*words))
print("rolled packed recovery circuit: %d batches of 7 (listing interpreter, compiled blocks, scalar), %d differences; ops executed %d, instructions %d, flat length %d" % (tot, bad, ops, instr, len(fn.flat)))
