'''(a) fundamental rotation cycles of the cycle's addition graph (why no single frame aligns the carry graph);
(b) per-word lookahead (in-flight guessed bits) of the best 32-bit sweep found;
(c) replay validation of the 32-bit schedule on the real instances: for every GPU root in split_e3/roots_2.txt the
    schedule path with all guesses set to the true bits passes every check (completeness), and for random non-roots
    it fails (soundness); each root has exactly one path (all guessed bits/carries are functions of g).
usage: python analyze.py'''

# Publication path adapter: resolve data paths from the extracted source tree.
def _hca_public_path_text(value):
    if "__HCA_WORKSPACE__/" not in value:
        return value
    import os as _hca_os
    from pathlib import Path as _hca_Path
    root = _hca_os.environ.get("HASHCYBERAXE_WORKSPACE")
    if root is None:
        here = _hca_Path(__file__).resolve().parent
        root = next((str(p) for p in (here, *here.parents) if (p / "research").is_dir()), None)
    if root is None:
        raise FileNotFoundError("Extract the research source tree, or set HASHCYBERAXE_WORKSPACE to its archive directory.")
    return value.replace("__HCA_WORKSPACE__/", str(_hca_Path(root).resolve()).replace("\\", "/") + "/")

import sys, random, math
sys.dont_write_bytecode = True
import cyc, sched
M = cyc.M
FR32 = {'Y12': 8, 'd1': 0, 'a1': 0, 'Dd1': 16, 'w10': 0, 'C1a1': 8, 'C1c1': 20, 'Y1': 0, 'chk': 20}

def cycles():
    E = []
    for name, ops, c in sched.SP:
        for terms, xc in ops:
            for w, r in terms: E.append((w, name, r))
    # alignment: consumer Z bit i reads W bit i-r; frames aligned iff pos(Z) = pos(W) + r  (pos = rotation offset)
    pos = {'g': 0}; tree = []; rest = []
    for w, z, r in E:
        if z not in pos and w in pos: pos[z] = (pos[w] + r) % 32; tree.append((w, z, r))
        else: rest.append((w, z, r))
    return E, tree, [(w, z, r, (pos[w] + r - pos[z]) % 32) for w, z, r in rest], pos

def inflight(fr):
    ev, levs = sched.schedule(32, fr)
    per = {}; live = {}; peakw = {}
    for e in ev:
        if e[0] == 'G' and e[1] != 'g': live[e[1]] = live.get(e[1], 0) + 1; per[e[1]] = per.get(e[1], 0) + 1
        if e[0] == 'A' and e[3] == 1: live[e[1]] -= 1
        for w, c in live.items(): peakw[w] = max(peakw.get(w, 0), c)
    return per, peakw, max(levs)

def replay(ev, P, g):
    v = cyc.eval_adds(P, g); A = {name: (ops, c) for name, ops, c in cyc.ADDS(P)}
    carry = {}; gcarry = {}; known = {}
    for e in ev:
        t = e[0]
        if t == 'G': known[(e[1], e[2])] = (v[e[1]] >> e[2]) & 1
        elif t == 'C':
            name = e[1]; ops, c = A[name]; j0 = None
            # true carry entering the first processed bit: recompute from the word values
            f = FR32[name] % 32; j0 = (32 - f) % 32
            s = (c & ((1 << j0) - 1))
            for terms, xc in ops:
                x = xc
                for w, r in terms: x ^= cyc.rol(v[w], r)
                s += x & ((1 << j0) - 1)
            carry[name] = gcarry[name] = s >> j0
        elif t == 'Z': carry[e[1]] = 0
        elif t == 'A':
            name, j, mode = e[1], e[2], e[3]; ops, c = A[name]; s = carry[name] + ((c >> j) & 1)
            for terms, xc in ops:
                b = (xc >> j) & 1
                for w, r in terms:
                    jj = (j - r) % 32
                    if (w, jj) not in known: return 'unknown bit %s.%d used' % (w, jj)
                    b ^= known[(w, jj)]
                s += b
            o = s & 1; carry[name] = s >> 1
            if mode == 2:
                if o: return 'chk'
            elif mode == 1:
                if known[(name, j)] != o: return 'verify'
            else: known[(name, j)] = o
        elif t == 'V':
            if carry[e[1]] != gcarry[e[1]]: return 'carry'
    return 'ok'

if __name__ == '__main__':
    E, tree, rest, pos = cycles()
    print('(a) addition graph: %d nodes, %d rotation edges, %d independent cycles' % (len(pos), len(E), len(rest)))
    for w, z, r, m in rest:
        print('    cycle closed by %-5s -> %-5s (rot %2d): net rotation %2d (lookahead >= %d bits on this cycle)' % (w, z, r, m, min(m, 32 - m)))
    per, peakw, pk = inflight(FR32)
    print('(b) best sweep frames', FR32, 'peak level %.2f' % pk)
    print('    bits guessed ahead per word:', per, ' max simultaneously in flight per word:', peakw, ' sum', sum(peakw.values()))
    ev, _ = sched.schedule(32, FR32)
    L = open(_hca_public_path_text('__HCA_WORKSPACE__/research/fifties/split_e3/inst_2.txt')).read().split('\n')
    R = open(_hca_public_path_text('__HCA_WORKSPACE__/research/fifties/split_e3/roots_2.txt')).read().split('\n')
    rnd = random.Random(9); nr = ok = nonroot = rej = 0; bad = []
    for li, ri in zip(L, R):
        if not li.strip(): continue
        p = li.split(); r = ri.split(); assert p[0] == r[0]
        P = [int(x, 16) for x in p[1:]]
        for x in r[2:]:
            nr += 1; res = replay(ev, P, int(x, 16)); ok += res == 'ok'
            if res != 'ok': bad.append((p[0], x, res))
        for _ in range(2):
            g = rnd.getrandbits(32)
            if g in [int(x, 16) for x in r[2:]]: continue
            nonroot += 1; rej += replay(ev, P, g) != 'ok'
    print('(c) replay on %d real instances: GPU roots %d, schedule path passes for %d; random non-roots %d, rejected %d; failures %s'
          % (len([l for l in L if l.strip()]), nr, ok, nonroot, rej, bad[:5]))
