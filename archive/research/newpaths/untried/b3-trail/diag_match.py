#!/usr/bin/env python3
"""diag_match.py - last step only: given the state difference after the round-1 column step
(u0..u15) and the message differences, model the four round-1 diagonal G calls with the
collision condition dv[i] = dv[i+8] and LM weight <= W. Writes runs/NAME.cnf / .map.json in
b3trail's format (decode.py reads it).  Used to price the last step for fixed column trails.

usage: diag_match.py --u HEX16 --dm HEX16 --W N --out runs/NAME
"""
import argparse
import json

from b3trail import Builder, PERM, neg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--u', required=True, help='16 comma-separated hex words (state before round-1 diagonals)')
    ap.add_argument('--dm', required=True, help='16 comma-separated hex message differences (unpermuted)')
    ap.add_argument('--W', type=int, required=True)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    U = [int(t, 16) for t in args.u.split(',')]
    DM = [int(t, 16) for t in args.dm.split(',')]
    b = Builder(order='best')
    v = [b.const(x) for x in U]
    m = [b.const(x) for x in DM]
    for i in range(16):
        b.name(f'm{i}', m[i])
    m1 = [m[i] for i in PERM]  # round-1 schedule
    b.G(v, 0, 5, 10, 15, m1[8], m1[9], 'r1d0')
    b.G(v, 1, 6, 11, 12, m1[10], m1[11], 'r1d1')
    b.G(v, 2, 7, 8, 13, m1[12], m1[13], 'r1d2')
    b.G(v, 3, 4, 9, 14, m1[14], m1[15], 'r1d3')
    for i in range(16):
        b.name(f'out.v{i}', v[i])
    for i in range(8):
        for l1, l2 in zip(v[i], v[i + 8]):
            b.clause([neg(l1), l2])
            b.clause([l1, neg(l2)])
    nweights = len(b.weights)
    if args.W >= 0:
        b.at_most(b.weights, args.W)
    with open(args.out + '.cnf', 'w') as fh:
        fh.write(f'p cnf {b.nv} {len(b.cl)}\n')
        fh.write(''.join(' '.join(map(str, c)) + ' 0\n' for c in b.cl))
    json.dump({'args': vars(args), 'adds': b.adds, 'words': b.words, 'gcalls': b.gcalls},
              open(args.out + '.map.json', 'w'))
    print(f'vars={b.nv} clauses={len(b.cl)} weight_lits={nweights} lm_adds={len(b.adds)}', flush=True)


if __name__ == '__main__':
    main()
