#!/usr/bin/env python3
"""Step-1 (dense part) CNF for the 38-step SHA-256 characteristic of ePrint 2026/1120 (scout2-1, research only).

Unknowns: A0..A15, E4..E15, W8..W15 of member x; member y = x XOR the Table-3 differences (shared literals).
Constraints, all CV-free (rows -4..3 and W0..W7 are left to Step 2, which connects any chaining value):
  * step relations rows 4..15 for both members: A_i = E_i - A_{i-4} + S0(A_{i-1}) + MAJ(..) (i = 4..15) and
    E_i = W_i + A_{i-4} + E_{i-4} + S1(E_{i-1}) + CH(..) + K_i (i = 8..15);
  * every A/E cell of rows 4..15, every W cell of rows 8..15, the '+' pairs;
  * message expansion: s0 differences of W8..W11 (W23..W26), s1(W15) (dW17 = 0) and s0(W15) (dW30 = 0);
  * row-16 modular differences dE16, dA16 (the L* conditions), as published-pair constants.
Option --row16: also row 16 with a free W16 (cells, two-bit conditions keyed at row 16): G nonempty.
Option --fix-published / --fix-published-flip=A13:5 : unit clauses fixing A0..A15 (x) (self-tests).
Option --block=FILE.json : forbid the A3..A13 (x) cores listed in FILE (a JSON list of solutions).

  python gen_step1.py cnf OUT.cnf [options]        -> OUT.cnf and OUT.cnf.map.json
  python gen_step1.py decode OUT.cnf KISSAT_OUTPUT  -> verifies, prints and appends the solution to OUT.sols.json
  python gen_step1.py check                         -> published S passes the Python-side conditions
"""
import sys, json, os
from r38core import *

class Enc:
    def __init__(self):
        self.n = 1; self.T = 1; self.cls = [[1]]; self.cache = {}
    def var(self):
        self.n += 1; return self.n
    def add(self, c):
        T = self.T; out = []
        for l in c:
            if l == T: return
            if l == -T: continue
            if -l in out: return
            if l not in out: out.append(l)
        if not out: raise ValueError('empty clause')
        self.cls.append(out)
    # ---- gates ----
    def xorN(self, lits):
        par = 0; vs = {}
        for l in lits:
            if abs(l) == self.T:
                par ^= (l == self.T); continue
            if l < 0: par ^= 1
            v = abs(l); vs[v] = vs.get(v, 0) ^ 1
        vs = sorted(v for v, c in vs.items() if c)
        if not vs: return self.T if par else -self.T
        if len(vs) == 1: return -vs[0] if par else vs[0]
        if len(vs) > 3:   # chain
            r = self.xorN([self.xorN(vs[:3])] + vs[3:])
            return -r if par else r
        key = ('x',) + tuple(vs)
        if key not in self.cache:
            z = self.var(); k = len(vs)
            for a in range(1 << k):
                p = bin(a).count('1') & 1
                self.add([(-vs[j] if (a >> j) & 1 else vs[j]) for j in range(k)] + [z if p else -z])
            self.cache[key] = z
        z = self.cache[key]
        return -z if par else z
    def mux(self, e, f, g):   # e ? f : g
        T = self.T
        if e == T: return f
        if e == -T: return g
        if f == g: return f
        if f == -g: return -self.xorN([e, f])
        key = ('m', e, f, g)
        if key not in self.cache:
            z = self.var()
            for c in ([-e, -f, z], [-e, f, -z], [e, -g, z], [e, g, -z], [-f, -g, z], [f, g, -z]): self.add(c)
            self.cache[key] = z
        return self.cache[key]
    def maj(self, a, b, c):
        T = self.T
        if a == b or a == c: return a
        if b == c: return b
        if a == -b: return c
        if a == -c: return b
        if b == -c: return a
        key = ('j',) + tuple(sorted((a, b, c)))
        if key not in self.cache:
            z = self.var()
            for cl in ([-a, -b, z], [-a, -c, z], [-b, -c, z], [a, b, -z], [a, c, -z], [b, c, -z]): self.add(cl)
            self.cache[key] = z
        return self.cache[key]
    def and2(self, a, b):
        T = self.T
        if a == -T or b == -T or a == -b: return -T
        if a == T: return b
        if b == T or a == b: return a
        key = ('a',) + tuple(sorted((a, b)))
        if key not in self.cache:
            z = self.var()
            for cl in ([-z, a], [-z, b], [z, -a, -b]): self.add(cl)
            self.cache[key] = z
        return self.cache[key]
    # ---- words (lists of 32 literals, index = bit) ----
    def fresh(self): return [self.var() for _ in range(32)]
    def rot(self, w, n): return [w[(b + n) % 32] for b in range(32)]
    def shr(self, w, n): return [w[b + n] if b + n < 32 else -self.T for b in range(32)]
    def lin(self, ws): return [self.xorN([w[b] for w in ws]) for b in range(32)]
    def S0(self, w): return self.lin([self.rot(w, 2), self.rot(w, 13), self.rot(w, 22)])
    def S1(self, w): return self.lin([self.rot(w, 6), self.rot(w, 11), self.rot(w, 25)])
    def s0(self, w): return self.lin([self.rot(w, 7), self.rot(w, 18), self.shr(w, 3)])
    def s1(self, w): return self.lin([self.rot(w, 17), self.rot(w, 19), self.shr(w, 10)])
    def CH(self, e, f, g): return [self.mux(e[b], f[b], g[b]) for b in range(32)]
    def MAJ(self, a, b, c): return [self.maj(a[b_], b[b_], c[b_]) for b_ in range(32)]
    def NOT(self, w): return [-l for l in w]
    def ltw(self, a, b):
        """literal: a < b as unsigned 32-bit words."""
        T = self.T; eq = T; terms = []
        for i in range(31, -1, -1):
            terms.append(self.and2(eq, self.and2(-a[i], b[i])))
            eq = self.and2(eq, -self.xorN([a[i], b[i]]))
        terms = [t for t in terms if t != -T]
        if T in terms: return T
        z = self.var()
        self.add([-z] + terms)
        for t in terms: self.add([z, -t])
        return z
    def const(self, v): return [self.T if (v >> b) & 1 else -self.T for b in range(32)]
    def addw(self, ops, k=0, target=None):
        """sum of words + constant k mod 2^32 by column compression; tie to target if given."""
        T = self.T
        cols = [[] for _ in range(33)]
        for w in ops:
            for b in range(32):
                if w[b] != -T: cols[b].append(w[b])
        for b in range(32):
            if (k >> b) & 1: cols[b].append(T)
        out = []
        for b in range(32):
            col = cols[b]
            t = sum(1 for l in col if l == T); col = [l for l in col if l != T]
            if t // 2: cols[b + 1].extend([T] * (t // 2))
            if t % 2: col.append(T)
            if b == 31:
                out.append(self.xorN(col)); break
            while len(col) > 1:
                if len(col) >= 3:
                    x, y, z = col[0], col[1], col[2]; col = col[3:]
                    s = self.xorN([x, y, z]); c = self.maj(x, y, z)
                else:
                    x, y = col[0], col[1]; col = col[2:]
                    s = self.xorN([x, y]); c = self.and2(x, y)
                col.append(s)
                if c != -T: cols[b + 1].append(c)
            out.append(col[0] if col else -T)
        if target is not None:
            for b in range(32):
                self.add([-out[b], target[b]]); self.add([out[b], -target[b]])
        return out

def sign_units(D, Tgt):
    """For f(W^x) XOR f(W^y) = D and f(W^x) - f(W^y) = Tgt (mod 2^32): required f(W^x) bits at the support of D
    (bit 31 free).  Returns {bit: value}; raises if no sign pattern fits."""
    bits = [b for b in range(32) if (D >> b) & 1]
    sols = []
    if len(bits) <= 22:
        for a in range(1 << len(bits)):
            s = 0
            for j, b in enumerate(bits): s += (1 << b) if (a >> j) & 1 else -(1 << b)
            if s & M == Tgt: sols.append(a)
    if not sols: raise ValueError('no sign pattern for D=%08x T=%08x' % (D, Tgt))
    req = {}
    for j, b in enumerate(bits):
        vals = {(a >> j) & 1 for a in sols}
        if len(vals) == 1: req[b] = vals.pop()
    return req

def build(row16=False, fix=None, block=(), copies=1, drop='', gcopies=1):
    """copies = k: k copies of rows 14, 15 (E14, E15 and what depends on them) sharing rows 0..13, pairwise
    distinct in (E14, E15): SAT iff some dense part has |L*| >= k (with row16: each copy also has a W16 in G)."""
    e = Enc(); T = e.T
    def word(kind, i, prev=None):
        m, v, d, p = CELL[kind][i]
        w = []
        for b in range(32):
            if (m >> b) & 1: w.append(T if (v >> b) & 1 else -T)
            elif kind == 'E' and (PLUS[i] >> b) & 1 and prev is not None: w.append(prev[b])
            else: w.append(e.var())
        return w
    def ymask(w, kind, i):
        d = CELL[kind][i][2]
        return [(-l if (d >> b) & 1 else l) for b, l in enumerate(w)]
    def rel_A(mem, i):
        done = set()
        for (A_, E_, W_) in mem:
            key = tuple(E_[i]) + tuple(A_[i-4]) + tuple(A_[i-1]) + tuple(A_[i-2]) + tuple(A_[i-3]) + tuple(A_[i])
            if key in done: continue
            done.add(key)
            e.addw([E_[i], e.NOT(A_[i-4]), e.S0(A_[i-1]), e.MAJ(A_[i-1], A_[i-2], A_[i-3])], 1, target=A_[i])
    def rel_E(mem, i):
        for (A_, E_, W_) in mem:
            e.addw([W_[i], A_[i-4], E_[i-4], e.S1(E_[i-1]), e.CH(E_[i-1], E_[i-2], E_[i-3])], K[i], target=E_[i])
    nunits = [0]
    def signs(Wx, name, f, i):
        fx = getattr(e, f)(Wx[i]); D = (s0 if f == 's0' else s1)(CELL['W'][i][2])
        for b, val in sign_units(D, REF[name]).items():
            e.add([fx[b] if val else -fx[b]]); nunits[0] += 1
    Ax = {i: word('A', i) for i in range(14)}
    Ex = {}
    for i in range(4, 14): Ex[i] = word('E', i, Ex.get(i - 1))
    relaxW = 'W' in drop     # W8..W10: package validity (modular dW, ds0W only), no XOR cells
    Wx = {i: (e.fresh() if relaxW and i <= 10 else word('W', i)) for i in range(8, 14)}
    Ay = {i: ymask(Ax[i], 'A', i) for i in Ax}; Ey = {i: ymask(Ex[i], 'E', i) for i in Ex}
    Wy = {i: (e.fresh() if relaxW and i <= 10 else ymask(Wx[i], 'W', i)) for i in Wx}
    mem = ((Ax, Ex, Wx), (Ay, Ey, Wy))
    for i in range(4, 14): rel_A(mem, i)
    for i in range(8, 14): rel_E(mem, i)
    for name, f, i in (('s0W8', 's0', 8), ('s0W9', 's0', 9), ('s0W10', 's0', 10), ('s0W11', 's0', 11)):
        if relaxW and i <= 10:
            e.addw([Wy[i]], md(TX[2][i], TY[2][i]), target=Wx[i])
            e.addw([e.s0(Wy[i])], REF[name], target=e.s0(Wx[i]))
        else:
            signs(Wx, name, f, i)
    cps = []
    for c in range(copies):
        Axc, Exc, Wxc = dict(Ax), dict(Ex), dict(Wx)
        Axc[14] = word('A', 14); Axc[15] = word('A', 15)
        Exc[14] = word('E', 14, Exc[13]); Exc[15] = word('E', 15, Exc[14])
        Wxc[14] = word('W', 14); Wxc[15] = word('W', 15)
        Ayc, Eyc, Wyc = dict(Ay), dict(Ey), dict(Wy)
        for i in (14, 15):
            Ayc[i] = ymask(Axc[i], 'A', i); Eyc[i] = ymask(Exc[i], 'E', i); Wyc[i] = ymask(Wxc[i], 'W', i)
        memc = ((Axc, Exc, Wxc), (Ayc, Eyc, Wyc))
        for i in (14, 15): rel_A(memc, i)
        for i in (14, 15): rel_E(memc, i)
        signs(Wxc, 's1W15', 's1', 15); signs(Wxc, 's0W15', 's0', 15)
        # row-16 modular differences: P^x - P^y = REF P, R^x - R^y = REF R
        Px = e.fresh(); Rx = e.fresh()
        e.addw([Axc[12], Exc[12], e.S1(Exc[15]), e.CH(Exc[15], Exc[14], Exc[13])], 0, target=Px)
        if 'P' not in drop: e.addw([Ayc[12], Eyc[12], e.S1(Eyc[15]), e.CH(Eyc[15], Eyc[14], Eyc[13])], REF['P'], target=Px)
        e.addw([e.S0(Axc[15]), e.MAJ(Axc[15], Axc[14], Axc[13])], 0, target=Rx)
        if 'R' not in drop: e.addw([e.S0(Ayc[15]), e.MAJ(Ayc[15], Ayc[14], Ayc[13])], REF['R'], target=Rx)
        extra = {}
        w16all = []
        for g in range((max(1, gcopies) if c == 0 else 1) if row16 else 0):
            W16 = word('W', 16); E16 = word('E', 16, Exc[15]); A16 = word('A', 16)
            W16y = ymask(W16, 'W', 16); E16y = ymask(E16, 'E', 16); A16y = ymask(A16, 'A', 16)
            e.addw([Px, W16], K[16], target=E16)
            e.addw([Px, W16y], (K[16] - REF['P']) & M, target=E16y)
            e.addw([E16, e.NOT(Axc[12]), Rx], 1, target=A16)
            e.addw([E16y, e.NOT(Ayc[12]), Rx], (1 - REF['R']) & M, target=A16y)
            V = {'A': {**Axc, 16: A16}, 'E': {**Exc, 16: E16}, 'W': {**Wxc, 16: W16}}
            for k1, i1, b1, ne, k2, i2, b2 in XROW.get(16, ()):
                l1, l2 = V[k1][i1][b1], V[k2][i2][b2]
                if ne: e.add([l1, l2]); e.add([-l1, -l2])
                else: e.add([-l1, l2]); e.add([l1, -l2])
            if g == 0: extra = {'W16': W16, 'E16': E16, 'A16': A16}
            if w16all: e.add([e.ltw(w16all[-1], W16)])     # strictly increasing W16 copies: |G| >= gcopies
            w16all.append(W16)
        if len(w16all) > 1: extra['W16all'] = w16all
        cps.append((Axc, Exc, Wxc, extra))
    for c1 in range(copies):
        for c2 in range(c1 + 1, copies):
            ds = [e.xorN([cps[c1][1][i][b], cps[c2][1][i][b]]) for i in (14, 15) for b in range(32)]
            e.add(ds)
    Ax, Ex, Wx, extra = cps[0]
    nunits = nunits[0]
    if fix is not None:
        for i in range(16):
            for b in range(32): e.add([Ax[i][b] if (fix[i] >> b) & 1 else -Ax[i][b]])
    for core in block:
        cl = []
        for i in range(3, 14):
            for b in range(32): cl.append(-Ax[i][b] if (core[i] >> b) & 1 else Ax[i][b])
        e.add(cl)
    wm = {'A': {i: Ax[i] for i in Ax}, 'E': {i: Ex[i] for i in Ex}, 'W': {i: Wx[i] for i in Wx}, 'extra': extra,
          'copies': [{'A14': c[0][14], 'A15': c[0][15], 'W14': c[2][14], 'W15': c[2][15]} for c in cps]}
    return e, wm, nunits

def write_cnf(path, e, wm, meta):
    with open(path, 'w', newline='\n') as f:
        f.write('c scout2-1 Step-1 CNF r38 %s\n' % json.dumps(meta))
        f.write('p cnf %d %d\n' % (e.n, len(e.cls)))
        for c in e.cls: f.write(' '.join(map(str, c)) + ' 0\n')
    with open(path + '.map.json', 'w') as f: json.dump({'wm': wm, 'meta': meta}, f)

def read_model(path):
    sat = None; asg = {}
    with open(path) as f:
        for line in f:
            if line.startswith('s '): sat = line.split()[1]
            elif line.startswith('v '):
                for t in line.split()[1:]:
                    v = int(t)
                    if v: asg[abs(v)] = v > 0
    return sat, asg

def wordval(w, asg):
    x = 0
    for b, l in enumerate(w):
        bit = True if l == 1 else False if l == -1 else (asg[abs(l)] if l > 0 else not asg[abs(l)])
        x |= int(bit) << b
    return x

def main():
    cmd = sys.argv[1]
    if cmd == 'check':
        X, Y = TX, TY
        Xd = ({i: X[0][i] for i in range(16)}, {i: X[1][i] for i in range(4, 16)}, {i: X[2][i] for i in range(8, 16)})
        Yd = ({i: Y[0][i] for i in range(16)}, {i: Y[1][i] for i in range(4, 16)}, {i: Y[2][i] for i in range(8, 16)})
        print('REF', {k: '%08x' % v for k, v in REF.items()})
        print('published S dense_checks failures:', dense_checks(Xd, Yd))
        X2, Y2 = dense_from_A([TX[0][i] for i in range(16)])
        print('dense_from_A reproduces published:', X2 == Xd and Y2 == Yd)
        ok, same, d16, d17, _ = end_to_end(X2, Y2, PCV)
        print('end-to-end on published CV: rows0..15 ok', ok, 'W0..W6 equal', same, 'dW16 %08x dW17 %08x' % (d16, d17))
        for name, f, i in (('s0W8', s0, 8), ('s0W9', s0, 9), ('s0W10', s0, 10), ('s0W11', s0, 11), ('s1W15', s1, 15), ('s0W15', s0, 15)):
            req = sign_units(f(CELL['W'][i][2]), REF[name]); fx = f(TX[2][i])
            assert all(((fx >> b) & 1) == v for b, v in req.items()), name
            print(' %s: %d sign units, published satisfies them' % (name, len(req)))
        return
    if cmd == 'cnf':
        out = sys.argv[2]; opts = sys.argv[3:]
        row16 = '--row16' in opts; fix = None; block = []; copies = 1; drop = ''; gcopies = 1
        for o in opts:
            if o.startswith('--drop='): drop = o.split('=')[1]
            if o.startswith('--gcopies='): gcopies = int(o.split('=')[1])
            if o.startswith('--copies='): copies = int(o.split('=')[1])
            if o == '--fix-published': fix = [TX[0][i] for i in range(16)]
            if o.startswith('--fix-published-flip='):
                k, b = o.split('=')[1].split(':'); fix = [TX[0][i] for i in range(16)]
                fix[int(k[1:])] ^= 1 << int(b)
            if o.startswith('--fix='):
                fn, j = o.split('=', 1)[1].rsplit(':', 1)
                s = json.load(open(fn))[int(j)]; fix = [s['Ax'][str(i)] for i in range(16)]
            if o.startswith('--block='):
                block = [{int(i): v for i, v in s['Ax'].items()} for s in json.load(open(o.split('=', 1)[1]))]
        e, wm, nunits = build(row16, fix, block, copies, drop, gcopies)
        meta = {'row16': row16, 'fix': fix is not None, 'block': len(block), 'units_sign': nunits, 'copies': copies, 'drop': drop, 'gcopies': gcopies}
        write_cnf(out, e, wm, meta)
        print('wrote', out, 'vars', e.n, 'clauses', len(e.cls), meta)
        return
    if cmd == 'decode':
        cnf, outp = sys.argv[2], sys.argv[3]
        mp = json.load(open(cnf + '.map.json')); wm = mp['wm']
        sat, asg = read_model(outp)
        print('status', sat)
        if sat != 'SATISFIABLE': return
        Ax = [wordval(wm['A'][str(i)], asg) for i in range(16)]
        Exs = {i: wordval(wm['E'][str(i)], asg) for i in range(4, 16)}
        Wxs = {i: wordval(wm['W'][str(i)], asg) for i in range(8, 16)}
        X, Y = dense_from_A(Ax)
        cons = all(X[1][i] == Exs[i] for i in Exs) and all(X[2][i] == Wxs[i] for i in Wxs)
        bad = dense_checks(X, Y)
        ok, same, d16, d17, _ = end_to_end(X, Y, PCV)
        core_same = all(Ax[i] == TX[0][i] for i in range(3, 14))
        diff_rows = [i for i in range(16) if Ax[i] != TX[0][i]]
        print('CNF words consistent with recomputation:', cons)
        print('independent dense_checks failures:', bad)
        print('end-to-end (published CV): rows0..15', ok, 'W0..W6 equal', same, 'dW16 %08x dW17 %08x' % (d16, d17))
        print('A3..A13 equal to published:', core_same, ' rows where A differs from published:', diff_rows)
        print('Ax', ' '.join('%08x' % a for a in Ax))
        sol = {'Ax': {i: Ax[i] for i in range(16)}, 'valid': (not bad) and cons and ok and same, 'core_same': core_same,
               'diff_rows': diff_rows, 'cnf': os.path.basename(cnf), 'out': os.path.basename(outp)}
        if mp['wm']['extra']:
            sol['W16'] = wordval(mp['wm']['extra']['W16'], asg)
            if 'W16all' in mp['wm']['extra']:
                sol['W16all'] = [wordval(w, asg) for w in mp['wm']['extra']['W16all']]
                print(' W16 copies:', len(sol['W16all']), 'distinct', len(set(sol['W16all'])))
        cp = []
        for c in mp['wm'].get('copies', [])[1:]:
            a14, a15 = wordval(c['A14'], asg), wordval(c['A15'], asg)
            Xc, Yc = dense_from_A(Ax[:14] + [a14, a15])
            badc = dense_checks(Xc, Yc)
            cp.append({'A14': a14, 'A15': a15, 'W14': Xc[2][14], 'W15': Xc[2][15], 'checks': badc})
            print(' copy: W14 %08x W15 %08x failures %s' % (Xc[2][14], Xc[2][15], badc))
        if cp:
            sol['copies'] = cp
            sol['valid'] = sol['valid'] and all(not c['checks'] for c in cp)
        print(' main copy: W14 %08x W15 %08x; solution valid: %s' % (X[2][14], X[2][15], sol['valid']))
        sp = os.path.splitext(cnf)[0] + '.sols.json'
        sols = json.load(open(sp)) if os.path.exists(sp) else []
        sols.append(sol); json.dump(sols, open(sp, 'w'), indent=1)
        print('appended to', sp)

if __name__ == '__main__':
    main()
