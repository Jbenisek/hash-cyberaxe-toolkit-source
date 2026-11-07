#!/usr/bin/env python3
"""b3trail.py - XOR-differential characteristic model for reduced-round BLAKE3 compression.

Writes a DIMACS CNF whose models are XOR-differential characteristics of the BLAKE3
compression function with R rounds (semantics of hash-smash/verifier/blake3.py):

  * fixed input-state difference: chaining value v0..v7 and IV words v8..v11 have no
    difference (both sides use IV), counter words v12/v13, block length v14 and flags v15
    get the XOR differences given on the command line;
  * free XOR message differences dm0..dm15 (optionally restricted to a subset), the same
    difference in both rounds (the schedule only permutes words);
  * every modular addition priced by Lipmaa-Moriai (2001): valid iff
    eq(a<<1,b<<1,c<<1) & (a^b^c^(b<<1)) == 0, weight HW(~eq(a,b,c) & 0x7fffffff);
  * a three-input addition a+b+x is two 2-input additions, either in code order
    ((a+b)+x) or best-of-three pairings (selector chooses which operand is added last);
  * collision on the 256-bit output: dv[i] ^ dv[i+8] = 0 for i < 8 (output words are
    v[i]^v[i+8]; no feed-forward in the first eight words);
  * total weight <= W (sequential counter, Sinz 2005).

Research tool only (our own team). Nothing here is filed or submitted.
"""
import argparse
import json
import sys

PERM = (2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8)
T, F = 'T', 'F'


def neg(l):
    if l == T:
        return F
    if l == F:
        return T
    return -l


class Builder:
    def __init__(self, n=32, order='best'):
        self.n = n
        self.order = order
        self.nv = 0
        self.cl = []
        self.weights = []
        self.wtag = []      # G-call tag of each weight literal
        self.adds = []      # every LM addition: inputs, output, guard, tag
        self.words = {}     # named words for printing
        self.gcalls = []    # per G call: names of words

    # ---------- basics ----------
    def new(self):
        self.nv += 1
        return self.nv

    def clause(self, lits):
        out = []
        for l in lits:
            if l == T:
                return
            if l == F:
                continue
            out.append(l)
        if not out:
            raise RuntimeError('empty clause: model UNSAT by construction')
        self.cl.append(out)

    def word(self):
        return [self.new() for _ in range(self.n)]

    def const(self, value):
        return [T if (value >> i) & 1 else F for i in range(self.n)]

    @staticmethod
    def is_zero(w):
        return all(l == F for l in w)

    def name(self, nm, w):
        self.words[nm] = w
        return w

    def xor(self, x, y):
        z = []
        for a, b in zip(x, y):
            if a in (T, F) and b in (T, F):
                z.append(T if (a == T) != (b == T) else F)
            elif a == F:
                z.append(b)
            elif b == F:
                z.append(a)
            elif a == T:
                z.append(neg(b))
            elif b == T:
                z.append(neg(a))
            else:
                c = self.new()
                self.clause([-c, a, b])
                self.clause([-c, -a, -b])
                self.clause([c, -a, b])
                self.clause([c, a, -b])
                z.append(c)
        return z

    def rotr(self, x, r):
        return [x[(i + r) % self.n] for i in range(self.n)]

    def _xor3(self, p, q, r, parity, extra):
        # forbid assignments of (p,q,r) whose xor != parity
        for vp in (0, 1):
            for vq in (0, 1):
                for vr in (0, 1):
                    if (vp ^ vq ^ vr) == parity:
                        continue
                    c = list(extra)
                    c.append(neg(p) if vp else p)
                    c.append(neg(q) if vq else q)
                    c.append(neg(r) if vr else r)
                    self.clause(c)

    # ---------- LM addition ----------
    def add2(self, a, b, guard=None, z=None, tag=''):
        n = self.n
        g = [] if guard is None else [neg(guard)]
        if self.is_zero(a) and self.is_zero(b):
            if z is None:
                return self.const(0)
            for i in range(n):
                self.clause(g + [neg(z[i])])
            return z
        if z is None:
            z = self.word()
        self._xor3(a[0], b[0], z[0], 0, g)
        for i in range(1, n):
            self._xor3(a[i], b[i], z[i], 0, g + [a[i - 1], b[i - 1], z[i - 1]])
            self._xor3(a[i], b[i], z[i], 1, g + [neg(a[i - 1]), neg(b[i - 1]), neg(z[i - 1])])
        for i in range(n - 1):
            w = self.new()
            self.clause(g + [neg(a[i]), b[i], w])
            self.clause(g + [a[i], neg(b[i]), w])
            self.clause(g + [neg(a[i]), z[i], w])
            self.clause(g + [a[i], neg(z[i]), w])
            self.weights.append(w)
            self.wtag.append(tag.split('.')[0])
        self.adds.append({'a': a, 'b': b, 'z': z, 'guard': guard, 'tag': tag})
        return z

    def add3(self, p, q, r, tag=''):
        zs = [self.is_zero(p), self.is_zero(q), self.is_zero(r)]
        if all(zs):
            return self.const(0)
        if sum(zs) == 2:
            nz = [w for w, iz in zip((p, q, r), zs) if not iz][0]
            return self.add2(self.const(0), nz, tag=tag + ':single')
        if self.order == 'code':
            t = self.add2(p, q, tag=tag + ':ab')
            return self.add2(t, r, tag=tag + ':abx')
        z = self.word()
        sels = [self.new() for _ in range(3)]
        self.clause(sels)
        for k, (u, v, last, lab) in enumerate(((p, q, r, 'ab+x'), (p, r, q, 'ax+b'),
                                              (q, r, p, 'bx+a'))):
            t = self.add2(u, v, guard=sels[k], tag=f'{tag}:{lab}:first')
            self.add2(t, last, guard=sels[k], z=z, tag=f'{tag}:{lab}:second')
        return z

    # ---------- BLAKE3 ----------
    def G(self, v, ia, ib, ic, id_, x, y, tag):
        A, B, C, D = v[ia], v[ib], v[ic], v[id_]
        rec = {'tag': tag, 'idx': [ia, ib, ic, id_]}
        for nm, w in (('a', A), ('b', B), ('c', C), ('d', D), ('x', x), ('y', y)):
            rec[nm] = self.name(f'{tag}.{nm}', w) and f'{tag}.{nm}'
        A = self.add3(A, B, x, tag=f'{tag}.s1')
        self.name(f'{tag}.a1', A)
        D = self.rotr(self.xor(D, A), 16)
        self.name(f'{tag}.d1', D)
        C = self.add2(C, D, tag=f'{tag}.s3')
        self.name(f'{tag}.c1', C)
        B = self.rotr(self.xor(B, C), 12)
        self.name(f'{tag}.b1', B)
        A = self.add3(A, B, y, tag=f'{tag}.s5')
        self.name(f'{tag}.a2', A)
        D = self.rotr(self.xor(D, A), 8)
        self.name(f'{tag}.d2', D)
        C = self.add2(C, D, tag=f'{tag}.s7')
        self.name(f'{tag}.c2', C)
        B = self.rotr(self.xor(B, C), 7)
        self.name(f'{tag}.b2', B)
        v[ia], v[ib], v[ic], v[id_] = A, B, C, D
        self.gcalls.append(rec)

    def compress(self, dv_in, dm, rounds):
        v = list(dv_in)
        m = list(dm)
        for r in range(rounds):
            self.G(v, 0, 4, 8, 12, m[0], m[1], f'r{r}c0')
            self.G(v, 1, 5, 9, 13, m[2], m[3], f'r{r}c1')
            self.G(v, 2, 6, 10, 14, m[4], m[5], f'r{r}c2')
            self.G(v, 3, 7, 11, 15, m[6], m[7], f'r{r}c3')
            self.G(v, 0, 5, 10, 15, m[8], m[9], f'r{r}d0')
            self.G(v, 1, 6, 11, 12, m[10], m[11], f'r{r}d1')
            self.G(v, 2, 7, 8, 13, m[12], m[13], f'r{r}d2')
            self.G(v, 3, 4, 9, 14, m[14], m[15], f'r{r}d3')
            m = [m[i] for i in PERM]
            if r == 0:
                self.s1 = list(v)
        return v

    def at_most(self, xs, k):
        n = len(xs)
        if k >= n:
            return
        if k == 0:
            for x in xs:
                self.clause([-x])
            return
        s = [[self.new() for _ in range(k)] for _ in range(n - 1)]
        self.clause([-xs[0], s[0][0]])
        for j in range(1, k):
            self.clause([-s[0][j]])
        for i in range(1, n - 1):
            self.clause([-xs[i], s[i][0]])
            self.clause([-s[i - 1][0], s[i][0]])
            for j in range(1, k):
                self.clause([-xs[i], -s[i - 1][j - 1], s[i][j]])
                self.clause([-s[i - 1][j], s[i][j]])
            self.clause([-xs[i], -s[i - 1][k - 1]])
        self.clause([-xs[n - 1], -s[n - 2][k - 1]])


def build(args):
    b = Builder(order=args.order)
    dv = [b.const(0) for _ in range(16)]
    dv[12] = b.const(args.dv12)
    dv[13] = b.const(args.dv13)
    dv[14] = b.const(args.dv14)
    dv[15] = b.const(args.dv15)
    if args.ctr_free:
        # the solver chooses the counter difference t (parent side has counter 0, so dt = t).
        # 'even': legal chunk-vs-parent position needs t even, t >= 2, t < 2^51 (data < 2^61 bytes)
        lo = b.word()
        hi = b.word() if args.ctr_free == 'lohi' else b.const(0)
        if args.ctr_free == 'lohi':
            for i in range(19, 32):
                b.clause([-hi[i]])
        if args.ctr_even:
            b.clause([-lo[0]])
        b.clause([l for l in lo + hi if l not in (T, F)])
        dv[12] = b.name('ctr.lo', lo)
        dv[13] = b.name('ctr.hi', hi)
    free = set(range(16)) if args.msg == 'all' else {int(t) for t in args.msg.split(',') if t != ''}
    fixed = {}
    if args.dm:
        for item in args.dm.split(','):
            k, v = item.split('=')
            fixed[int(k)] = int(v, 0)
    dm = []
    for i in range(16):
        if i in fixed:
            w = b.const(fixed[i])
        else:
            w = b.word() if i in free else b.const(0)
        dm.append(b.name(f'm{i}', w))
    out = b.compress(dv, dm, args.rounds)
    for i in range(16):
        b.name(f'out.v{i}', out[i])
    # output pairs: G4/G6 of the last step own digest words 0,2,5,7; G5/G7 own 1,3,4,6
    words_out = {'both': range(8), '46': (0, 2, 5, 7), '57': (1, 3, 4, 6), 'none': ()}[args.pairs]
    for i in words_out:
        for l1, l2 in zip(out[i], out[i + 8]):
            b.clause([neg(l1), l2])
            b.clause([l1, neg(l2)])
    if args.need_active:
        # at least one of the named calls has a nonzero output difference
        lits = []
        for t in args.need_active.split(','):
            for k in ('a2', 'b2', 'c2', 'd2'):
                lits += [l for l in b.words[f'{t}.{k}'] if l not in (T, F)]
        b.clause(lits)
    if args.s1 == 'nonzero' and args.rounds >= 2:
        # case NZ: some state bit differs after round 0
        b.clause([l for w in b.s1 for l in w if l not in (T, F)] +
                 [T] * any(l == T for w in b.s1 for l in w))
    if args.s1 == 'zero' and args.rounds >= 2:
        for w in b.s1:
            for l in w:
                b.clause([neg(l)])
    if args.nonzero_msg:
        # at least one message bit differs (used only for zero-input-difference studies)
        lits = [l for i in sorted(free) for l in dm[i] if l not in (T, F)]
        b.clause(lits)
    ws = b.weights
    if args.count:
        keep = set(args.count.split(','))
        ws = [w for w, t in zip(b.weights, b.wtag) if t in keep]
    nweights = len(ws)
    if args.W >= 0:
        b.at_most(ws, args.W)
    return b, nweights


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dv12', type=lambda s: int(s, 0), default=0)
    ap.add_argument('--dv13', type=lambda s: int(s, 0), default=0)
    ap.add_argument('--dv14', type=lambda s: int(s, 0), default=0)
    ap.add_argument('--dv15', type=lambda s: int(s, 0), default=0)
    ap.add_argument('--msg', default='all', help="'all' or comma list of message words allowed a difference")
    ap.add_argument('--rounds', type=int, default=2)
    ap.add_argument('--order', choices=('best', 'code'), default='best')
    ap.add_argument('--W', type=int, required=True)
    ap.add_argument('--nonzero-msg', action='store_true')
    ap.add_argument('--ctr-free', choices=('lo', 'lohi'), default=None,
                    help='counter difference chosen by the solver (v12, or v12 and v13)')
    ap.add_argument('--ctr-even', action='store_true', help='require t even (chunk-vs-parent legality)')
    ap.add_argument('--dm', default='', help="fix message differences, e.g. '6=1,7=1' (hex ok)")
    ap.add_argument('--s1', choices=('any', 'zero', 'nonzero'), default='any',
                    help='constrain the state difference after round 0 (case Z / case NZ split)')
    ap.add_argument('--pairs', choices=('both', '46', '57', 'none'), default='both',
                    help='which output words are required to collide (relaxations for bounds)')
    ap.add_argument('--count', default='', help='comma list of G tags whose weights count (default all)')
    ap.add_argument('--need-active', default='', help='comma list of G tags: at least one has nonzero output')
    ap.add_argument('--out', required=True, help='prefix for .cnf and .map.json')
    args = ap.parse_args()
    b, nweights = build(args)
    with open(args.out + '.cnf', 'w') as fh:
        fh.write(f'p cnf {b.nv} {len(b.cl)}\n')
        fh.write(''.join(' '.join(map(str, c)) + ' 0\n' for c in b.cl))
    meta = {'args': vars(args), 'nvars': b.nv, 'nclauses': len(b.cl), 'nweights': nweights,
            'adds': b.adds, 'words': b.words, 'gcalls': b.gcalls}
    with open(args.out + '.map.json', 'w') as fh:
        json.dump(meta, fh)
    print(f'vars={b.nv} clauses={len(b.cl)} weight_lits={nweights} lm_adds={len(b.adds)}', flush=True)


if __name__ == '__main__':
    main()
