#!/usr/bin/env python3
"""pair_free.py - universal price of one matched pair in the last step.

Two G calls P (plays G4 or G5) and Q (plays G6 or G7) with FREE input differences in all four
rows and (option) free message differences. The collision condition on their digest words is
out(P) = (c,d,a,b) of out(Q), i.e. P.a2=Q.c2, P.b2=Q.d2, P.c2=Q.a2, P.d2=Q.b2.  Q's output must be
nonzero (in every route that cancels inside round 0, some last-step call has a nonzero b/c
input, so by lemma L1 its output is nonzero).  Minimises LM weight of P plus Q.
Any 2-round characteristic whose last step contains such an active pair costs at least this.

usage: pair_free.py --W N --out runs/NAME [--msg free|zero] [--rows abcd|ac|bd]
"""
import argparse
import json

from b3trail import Builder, T, F, neg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--W', type=int, required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--msg', choices=('free', 'zero', 'Px'), default='free',
                    help="message differences: free in both calls, zero, or only P's x (CF route: G4 gets dm1)")
    ap.add_argument('--rows', default='abcd', help='rows allowed an input difference')
    ap.add_argument('--half', action='store_true',
                    help='add w(P) <= W/2 (valid only when P and Q are interchangeable: --msg zero)')
    args = ap.parse_args()
    b = Builder(order='best')
    rows = 'abcd'

    def inputs(tag):
        v = [b.word() if r in args.rows else b.const(0) for r in rows]
        for r, w in zip(rows, v):
            b.name(f'{tag}.in.{r}', w)
        x = b.word() if args.msg == 'free' or (args.msg == 'Px' and tag == 'P') else b.const(0)
        y = b.word() if args.msg == 'free' else b.const(0)
        return v, x, y
    vP, xP, yP = inputs('P')
    vQ, xQ, yQ = inputs('Q')
    stP = vP + [b.const(0)] * 12
    stQ = vQ + [b.const(0)] * 12
    b.G(stP, 0, 1, 2, 3, xP, yP, 'P')
    b.G(stQ, 0, 1, 2, 3, xQ, yQ, 'Q')
    outP, outQ = stP[:4], stQ[:4]
    swap = (2, 3, 0, 1)
    for k in range(4):
        for l1, l2 in zip(outP[k], outQ[swap[k]]):
            b.clause([neg(l1), l2])
            b.clause([l1, neg(l2)])
    b.clause([l for w in outQ for l in w if l not in (T, F)])
    nweights = len(b.weights)
    if args.W >= 0:
        b.at_most(b.weights, args.W)
        if args.half:
            # symmetric problem (same rows, no message difference): WLOG w(P) <= w(Q)
            b.at_most([w for w, t in zip(b.weights, b.wtag) if t == 'P'], args.W // 2)
    with open(args.out + '.cnf', 'w') as fh:
        fh.write(f'p cnf {b.nv} {len(b.cl)}\n')
        fh.write(''.join(' '.join(map(str, c)) + ' 0\n' for c in b.cl))
    json.dump({'args': vars(args), 'adds': b.adds, 'words': b.words, 'gcalls': b.gcalls},
              open(args.out + '.map.json', 'w'))
    print(f'vars={b.nv} clauses={len(b.cl)} weight_lits={nweights} lm_adds={len(b.adds)}', flush=True)


if __name__ == '__main__':
    main()
