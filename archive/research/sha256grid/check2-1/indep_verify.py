#!/usr/bin/env python3
"""check2-1 independent verifier for Step-1 dense parts of the 38-step SHA-256 characteristic (research only).

Independent of the scout's r38core.py functions: the characteristic is read from the package's vt38.py source text
(and compared field by field with the scout's r38core.py copy); SHA-256 is implemented here in a..h register form;
message words are obtained by inverting the step function from the published chaining value; the pair is then run
forward 38 steps and every CV-free Step-1 condition is checked on the actual trace.

  python3 indep_verify.py SOLS.json [SOLS.json ...]
"""

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

import ast, json, sys, os

VT = _hca_public_path_text('__HCA_WORKSPACE__/research/tools/build_pkg/scratch/pkgR38a/base/experiments/vt38.py')
SC = _hca_public_path_text('__HCA_WORKSPACE__/research/sha256grid/scout2-1/r38core.py')
NAMES = ('K', 'CHAR', 'TWOBIT', 'PCV', 'PMY', 'PMX')

def extract(path):
    tree = ast.parse(open(path).read())
    out = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            n = node.targets[0].id
            if n not in NAMES: continue
            v = node.value
            if isinstance(v, ast.Call) and isinstance(v.func, ast.Name) and v.func.id == '_h':
                out[n] = [int(t, 16) for t in v.args[0].value.split()]
            elif isinstance(v, ast.Call) and isinstance(v.func, ast.Name) and v.func.id == 'dict':
                out[n] = {kw.arg: ast.literal_eval(kw.value) for kw in v.keywords}
            else:
                out[n] = ast.literal_eval(v)
    return out

P = extract(VT); Q = extract(SC)
print('transcription: scout r38core.py vs package vt38.py:', {n: (P.get(n) == Q.get(n)) for n in NAMES})
K, CHAR, TWOBIT, PCV, PMY, PMX = (P[n] for n in NAMES)
MASK = 0xffffffff
R = 38
rotr = lambda x, n: ((x >> n) | (x << (32 - n))) & MASK
Sig0 = lambda x: rotr(x, 2) ^ rotr(x, 13) ^ rotr(x, 22)
Sig1 = lambda x: rotr(x, 6) ^ rotr(x, 11) ^ rotr(x, 25)
sig0 = lambda x: rotr(x, 7) ^ rotr(x, 18) ^ (x >> 3)
sig1 = lambda x: rotr(x, 17) ^ rotr(x, 19) ^ (x >> 10)
Ch = lambda e, f, g: ((e & f) ^ ((e ^ MASK) & g)) & MASK
Maj = lambda a, b, c: (a & b) ^ (a & c) ^ (b & c)

def parse(s):
    """cell string MSB first -> dict: fix (bit->x value), diff (bit->sign +1 for u / -1 for n), plus (set)."""
    fix, diff, plus = {}, {}, set()
    assert len(s) == 32
    for c, ch in enumerate(s):
        b = 31 - c
        if ch in '01': fix[b] = int(ch)
        elif ch == 'u': fix[b] = 1; diff[b] = +1
        elif ch == 'n': fix[b] = 0; diff[b] = -1
        elif ch == '+': plus.add(b)
        else: assert ch == '=', ch
    return fix, diff, plus

def cellof(kind, i): return parse(CHAR[kind].get(i, '=' * 32))
def xormask(kind, i): return sum(1 << b for b in cellof(kind, i)[1])
def signed(kind, i): return sum(s << b for b, s in cellof(kind, i)[1].items()) & MASK

def words_from_A(cv, A):
    """invert 16 steps: state a..h from cv, target new-a values A[0..15] -> W[0..15] and new-e values E[0..15]."""
    a, b, c, d, e, f, g, h = cv
    W, E = [], []
    for i in range(16):
        t2 = (Sig0(a) + Maj(a, b, c)) & MASK
        t1 = (A[i] - t2) & MASK
        w = (t1 - h - Sig1(e) - Ch(e, f, g) - K[i]) & MASK
        W.append(w)
        a, b, c, d, e, f, g, h = A[i], a, b, c, (d + t1) & MASK, e, f, g
        E.append(e)
    return W, E

def forward(cv, W16):
    W = list(W16)
    for i in range(16, R): W.append((sig1(W[i-2]) + W[i-7] + sig0(W[i-15]) + W[i-16]) & MASK)
    a, b, c, d, e, f, g, h = cv
    A, E = [], []
    for i in range(R):
        t1 = (h + Sig1(e) + Ch(e, f, g) + K[i] + W[i]) & MASK
        t2 = (Sig0(a) + Maj(a, b, c)) & MASK
        a, b, c, d, e, f, g, h = (t1 + t2) & MASK, a, b, c, (d + t1) & MASK, e, f, g
        A.append(a); E.append(e)
    return A, E, W

_PAx, _PEx, _PWx = forward(PCV, PMX); _PAy, _PEy, _PWy = forward(PCV, PMY)
REF_S0W10 = (sig0(_PWx[10]) - sig0(_PWy[10])) & MASK      # published pair's s0(W10) modular difference
_chk25 = ((sig1(_PWx[23]) - sig1(_PWy[23])) + REF_S0W10 + (_PWx[9] - _PWy[9]) + (_PWx[18] - _PWy[18])) & MASK
print('published pair: ds0(W10) = %08x; with its ds1(W23), dW9, dW18 it gives dW25 = %08x (characteristic %08x)'
      % (REF_S0W10, _chk25, sum(s << b for b, s in parse(CHAR['W'][25])[1].items()) & MASK))

def cell_ok(kind, i, x, y):
    fix, diff, _ = cellof(kind, i)
    if any(((x >> b) & 1) != v for b, v in fix.items()): return False
    return (x ^ y) == sum(1 << b for b in diff)

def md(x, y): return (x - y) & MASK

def check(Ax, cv=PCV):
    """returns (failures list, info dict) for member-x A0..A15 on chaining value cv."""
    Ay = [Ax[i] ^ xormask('A', i) for i in range(16)]
    Wx, Ex16 = words_from_A(cv, Ax); Wy, Ey16 = words_from_A(cv, Ay)
    TAx, TEx, TWx = forward(cv, Wx); TAy, TEy, TWy = forward(cv, Wy)
    bad = []
    if TAx[:16] != list(Ax) or TAy[:16] != Ay or TEx[:16] != Ex16 or TEy[:16] != Ey16: bad.append('inversion')
    for i in range(16):                       # rows 0..15: A and E cells (rows 0..4 must be difference-free)
        if not cell_ok('A', i, TAx[i], TAy[i]): bad.append('A%d' % i)
        if not cell_ok('E', i, TEx[i], TEy[i]): bad.append('E%d' % i)
        if i >= 1:
            pb = cellof('E', i)[2] & cellof('E', i - 1)[2]
            if any(((TEx[i] >> b) ^ (TEx[i-1] >> b)) & 1 for b in pb): bad.append('plus%d' % i)
    for i in range(7):
        if TWx[i] != TWy[i]: bad.append('dW%d!=0' % i)
    for i in range(8, 16):
        if not cell_ok('W', i, TWx[i], TWy[i]): bad.append('W%d' % i)
    # modular message conditions that depend only on the dense part (W7's modular difference is fixed by E7)
    if md(TWx[7], TWy[7]) != signed('W', 7): bad.append('dW7mod')
    if md(TWx[16], TWy[16]) != signed('W', 16): bad.append('dW16mod')
    if TWx[17] != TWy[17]: bad.append('dW17!=0')
    if md(TWx[23], TWy[23]) != signed('W', 23): bad.append('dW23mod')
    dW = lambda i: md(TWx[i], TWy[i])
    ds0 = lambda i: md(sig0(TWx[i]), sig0(TWy[i]))
    ds1 = lambda i: md(sig1(TWx[i]), sig1(TWy[i]))
    if (ds1(15) + dW(10)) & MASK: bad.append('s1W15 (dW17)')
    if ds0(8) != signed('W', 23): bad.append('s0W8 (dW23)')
    if (ds0(9) + dW(8)) & MASK: bad.append('s0W9 (dW24)')
    if ds0(10) != REF_S0W10: bad.append('s0W10 (dW25)')
    if (ds0(11) + dW(10)) & MASK: bad.append('s0W11 (dW26)')
    if (ds0(15) + signed('W', 23)) & MASK: bad.append('s0W15 (dW30)')
    # row-16 modular conditions (dE16 = signed E16 difference, dA16 = 0); CV-free because dW16 is fixed
    if md(TEx[16], TEy[16]) != signed('E', 16): bad.append('dE16mod')
    if md(TAx[16], TAy[16]) != signed('A', 16): bad.append('dA16mod')
    # CV-dependent (Step 2) items, reported only: W7 cell, dW22 = dW15 + ds0(W7)
    info = dict(W7cell=cell_ok('W', 7, TWx[7], TWy[7]), dW22zero=(TWx[22] == TWy[22]), W16=TWx[16],
                row16_on_this_cv=row16_ok(Ax, TWx[16]), Wx=['%08x' % w for w in TWx[:16]],
                W8_15=TWx[8:16])
    return bad, info

def row16_ok(Ax, W16x):
    """row 16 for both members given the dense part and a W16 value (W16^y = W16^x XOR the W16 cell difference):
    E16/A16/W16 cells, '+' pairs and every two-bit condition whose highest row is 16 (member x)."""
    Ay = [Ax[i] ^ xormask('A', i) for i in range(16)]
    vals = []
    for A, W16 in ((Ax, W16x), (Ay, W16x ^ xormask('W', 16))):
        # rows 12..15 E values from A (independent formula: E_i = A_i - T2_i + A_{i-4}, T2 from a..c)
        E = {}
        for i in range(4, 16):
            E[i] = (A[i] - (Sig0(A[i-1]) + Maj(A[i-1], A[i-2], A[i-3])) + A[i-4]) & MASK
        t1 = (E[12] + Sig1(E[15]) + Ch(E[15], E[14], E[13]) + K[16] + W16) & MASK   # h = E12 at step 16
        E16 = (A[12] + t1) & MASK
        A16 = (t1 + Sig0(A[15]) + Maj(A[15], A[14], A[13])) & MASK
        vals.append(({**{i: A[i] for i in range(16)}, 16: A16}, {**E, 16: E16}, W16))
    (Ax_, Ex_, Wx16), (Ay_, Ey_, Wy16) = vals
    if not (cell_ok('A', 16, Ax_[16], Ay_[16]) and cell_ok('E', 16, Ex_[16], Ey_[16]) and cell_ok('W', 16, Wx16, Wy16)):
        return False
    pb = cellof('E', 16)[2] & cellof('E', 15)[2]
    if any(((Ex_[16] >> b) ^ (Ex_[15] >> b)) & 1 for b in pb): return False
    V = {'A': Ax_, 'E': Ex_, 'W': {16: Wx16}}
    for k1, i1, b1, ne, k2, i2, b2 in TWOBIT:
        if max(i1, i2) != 16: continue
        if k1 == 'W' and i1 != 16 or k2 == 'W' and i2 != 16: return False   # not expected at row 16
        if ((V[k1][i1] >> b1) ^ (V[k2][i2] >> b2)) & 1 != ne: return False
    return True

if __name__ == '__main__':
    # published S*: derive its A0..A15 by running the published pair forward (no use of the scout's code)
    PAx, PEx, PWx = forward(PCV, PMX); PAy, PEy, PWy = forward(PCV, PMY)
    Sstar = PAx[:16]
    bad, info = check(Sstar)
    print('S* (published pair): failures', bad, '| W7 cell', info['W7cell'], '| dW22=0', info['dW22zero'], '| published W16 in row-16 set:',
          row16_ok(Sstar, PWx[16]), '| derived words equal published M\':', [int(w, 16) for w in info['Wx']] == PMX)
    cores = {'S*': Sstar}
    for fn in sys.argv[1:]:
        for j, s in enumerate(json.load(open(fn))):
            Ax = [s['Ax'][str(i)] if str(i) in s['Ax'] else s['Ax'][i] for i in range(16)]
            bad, info = check(Ax)
            import random
            rcv = [random.Random(1000 + j).getrandbits(32) for _ in range(8)]
            bad2, info2 = check(Ax, rcv)
            cvfree = (bad2 == bad and info2['W8_15'] == info['W8_15'])
            tag = '%s[%d]' % (os.path.basename(fn), j)
            same_rows = [i for i in range(16) if Ax[i] == Sstar[i]]
            print('%-26s failures %s | same on a random CV: %s | W7 cell / dW22=0 on published CV (Step 2): %s / %s | rows equal to S*: %s'
                  % (tag, bad, cvfree, info['W7cell'], info['dW22zero'], same_rows))
            g = s.get('W16all') or ([s['W16']] if 'W16' in s else [])
            if g:
                okg = [row16_ok(Ax, w) for w in g]
                print('   claimed row-16 W16 values: %d, distinct %d, all pass row 16: %s' % (len(g), len(set(g)), all(okg)))
            for c in s.get('copies', []):
                print('   copy W14 %08x W15 %08x' % (c['W14'], c['W15']))
            for name, Bx in cores.items():
                if Bx[3:14] == Ax[3:14] and name != 'S*': print('   same A3..A13 core as', name)
                top = 16
                while top > 0 and Bx[top - 1] == Ax[top - 1]: top -= 1
                if top < 16 and name != 'S*': print('   shares A%d..A15 with %s' % (top, name))
            cores[tag] = Ax
