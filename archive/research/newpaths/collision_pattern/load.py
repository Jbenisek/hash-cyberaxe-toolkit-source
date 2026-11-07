"""load.py: read hits.tsv and feat_out*.txt into numpy arrays (shared by check.py and analyse.py)."""
import os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
FCOLS = ['mode', 'set', 'g', 'k', 'y4', 'd1', 't', 'fail', 'coll'] + [f'w{j}' for j in range(16)] + \
        ['Y1', 'Y6', 'Y9', 'Y12', 'Y14', 'b1', 'a2', 'e1', 'h1', 'mass']


def hits():
    rows = [l.rstrip('\n').split('\t') for l in open(os.path.join(HERE, 'hits.tsv'))]
    cols = rows[0]
    return [dict(zip(cols, r)) for r in rows[1:]]


def feats(W):
    """returns dict kind -> (index list, array) with kind in 'h', 'n0', 'n1'; idx = hit number"""
    out = {}
    for line in open(os.path.join(HERE, f'feat_out{W}.txt')):
        f = line.split()
        tag = f[0]
        kind, i = ('h', int(tag[1:])) if tag[0] == 'h' else (tag[:2], int(tag[3:]))
        out.setdefault(kind, ([], []))
        out[kind][0].append(i)
        out[kind][1].append([int(x) for x in f[1:]])
    return {k: (np.array(v[0]), np.array(v[1], dtype=np.int64)) for k, v in out.items()}


def col(a, name):
    return a[:, FCOLS.index(name)]
