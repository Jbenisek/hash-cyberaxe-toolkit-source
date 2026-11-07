#!/usr/bin/env python3
"""ref.py (hotspot; research only) - scalar reference of the counter trial, independent of the GPU code paths:
outer_step ported from ctr_gen.cuh by text, the listed sets parsed from h8_deep.inc, and a record checker.
  python -B ref.py FILE.bin [N]   -> recompute N records (default 3000) from their basis words and c1, compare all fields
"""
import os, re, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
M = 0xFFFFFFFF
RECW = 40
F = dict(flags=0, misc=1, tid=2, olaunch=3, i=4, c1=5, d1=6, T0=7, C0d1=8, D2a1=9, D2b1=10, S11=11, S4=12, X9=13, Y4=14,
         w6=15, Y12=16, KY=17, C2b=18, C2c=19, C2a=20, C2d=21, K0d=22, w5=23, Y9=24, w8=25, e1=26, a1=27, y6=28, y14=29,
         h1=30, tau=31, eps=32, psi=33, eps3=34, r0=35, r1=36, r2=37, r3=38, ustart=39)
PX3, PX7, PX11, PX15, PW4, PW13 = 0x29D4FA98, 0xBEE3AF28, 0x44036000, 0x40C58500, 0x97475638, 0x0007C006
Y3A, Y3B, Y11A, Y11B = 0x8127c181, 0x7edf3e7e, 0x7af77f38, 0x850000c3
DELTA5 = 0xfffffff8
CM, CV, BETA_STAR = 0x0E09818B, 0x02008000, 0x18b0e098
RM = [0x00000001, 0x00000002, 0x00010000, 0x00020000, 0x00000404, 0x00000808, 0x01001008, 0x02002040]
RV = [0, 1, 0, 0, 1, 1, 0, 0]


def rol(v, n): v &= M; return ((v << n) | (v >> (32 - n))) & M
def ror(v, n): v &= M; return ((v >> n) | (v << (32 - n))) & M


def _outer_src():
    txt = open(os.path.join(HERE, 'ctr_gen.cuh')).read()
    body = txt[txt.index('outer_step(St *s) {'):]
    body = body[:body.index('\n}')]
    lines = []
    for ln in body.splitlines()[1:]:
        m = re.match(r'\s*s->(\w+) = (.*);\s*$', ln)
        if not m:
            continue
        e = re.sub(r'\b(0x[0-9a-fA-F]+|\d+)u\b', r'\1', m.group(2)).replace('s->', 's.')
        lines.append(f'    s.{m.group(1)} = ({e}) & M')
    return 'def outer_step(s):\n' + '\n'.join(lines) + '\n'


class S:
    pass


exec(_outer_src())


def outer(B):
    s = S()
    s.C0_d1, s.D2_a1, s.D2_b1, s.S11, s.S4, s.X9, s.Y4, s.w6 = B
    outer_step(s)
    return dict(Y12=s.Y12, KY=(s.Y1 + s.w12) & M, C2b=s.C2_b1, C2c=s.C2_c1, C2a=s.C2_a1, C2d=s.C2_d1, K0d=s.K0_d1,
                w5=s.w5, Y9=s.Y9, w8=s.w8, e1=(Y3A + s.Y4) & M)


def _lists():
    txt = open(os.path.join(HERE, 'h8_deep.inc')).read()
    e1 = {}
    for m in re.finditer(r'case (0x[0-9a-f]+)u: return (0x[0-9a-f]+)u \| \(\((.*?)\) \? 2u : 0u\) \| \(\((.*?)\) \? 4u : 0u\);', txt):
        beta, base = int(m.group(1), 16), int(m.group(2), 16)
        taus = {int(x, 16) for x in re.findall(r't == (0x[0-9a-f]+)u', m.group(3))}
        outs = {(int(a, 16), int(b, 16)) for a, b in re.findall(r't == (0x[0-9a-f]+)u && eps == (0x[0-9a-f]+)u', m.group(4))}
        e1[beta] = (base, taus, outs)
    e3 = {}
    for m in re.finditer(r'case (0x[0-9a-f]+)u: return \((.*?)\) \? (\d+)u : 0u;', txt):
        e3[int(m.group(1), 16)] = ({int(x, 16) for x in re.findall(r'psi == (0x[0-9a-f]+)u', m.group(2))}, int(m.group(3)))
    return e1, e3


E1L, E3L = _lists()


def e1_listed(beta, t, eps):
    if beta not in E1L:
        return 0
    base, taus, outs = E1L[beta]
    return base | (2 if t in taus else 0) | (4 if (t, eps) in outs else 0)


def e3_listed(psi, eps):
    if eps not in E3L:
        return 0
    s, code = E3L[eps]
    return code if psi in s else 0


def rule(h1, n=8):
    return all((bin(h1 & RM[i]).count('1') & 1) == RV[i] for i in range(n))


def trial(c1, o):
    """the inner trial of ctr_gpu.cu / hotspot.cu, scalar"""
    y4 = (o['e1'] - Y3A) & M
    d1 = (c1 - Y11A) & M
    a1 = rol(d1, 16) ^ o['Y12']; y6 = (a1 - o['KY']) & M; y14 = ((rol(y6, 7) ^ o['C2b']) - o['C2c']) & M
    w5, w5b, y9, w8 = o['w5'], (o['w5'] + DELTA5) & M, o['Y9'], o['w8']
    e1, e1b = o['e1'], (Y3B + y4) & M
    etaw = ror(e1 ^ e1b, 16)
    b1 = ror(y6 ^ c1, 12); a2 = (a1 + b1 + w5) & M; d2 = ror(d1 ^ a2, 8); c2 = (c1 + d2) & M; b2 = ror(b1 ^ c2, 7)
    c1b = (Y11B + d1) & M; b1b = ror(y6 ^ c1b, 12); a2b = (a1 + b1b + w5b) & M; d2b = ror(d1 ^ a2b, 8); c2b = (c1b + d2b) & M
    b2b = ror(b1b ^ c2b, 7)
    beta, tau, eps = b1 ^ b1b, a2 ^ a2b, c2 ^ c2b
    h1 = ror(y14 ^ e1, 16); g1 = (y9 + h1) & M; f1 = ror(y4 ^ g1, 12); e2 = (e1 + f1 + w8) & M; h2 = ror(h1 ^ e2, 8)
    g2 = (g1 + h2) & M; f2 = ror(f1 ^ g2, 7)
    h1b = ror(y14 ^ e1b, 16); g1b = (y9 + h1b) & M; f1b = ror(y4 ^ g1b, 12); e2b = (e1b + f1b + w8) & M; h2b = ror(h1b ^ e2b, 8)
    g2b = (g1b + h2b) & M; f2b = ror(f1b ^ g2b, 7)
    psi, eps3 = rol(f2 ^ f2b, 7) ^ g2 ^ g2b, e2 ^ e2b
    r0, r1, r2, r3 = a2 ^ g2 ^ a2b ^ g2b, e2 ^ c2 ^ e2b ^ c2b, f2 ^ d2 ^ f2b ^ d2b, b2 ^ h2 ^ b2b ^ h2b
    el, e3 = e1_listed(beta, tau, eps), e3_listed(psi, eps3)
    Y2 = rol(y14, 8) ^ o['C2d']; w0 = (Y2 - o['C2a'] - o['C2b']) & M
    K0a = (0x6a09e667 + 0x510e527f + w0) & M; T0 = rol(o['K0d'], 16) ^ K0a
    ra = rule(h1, 8); ga = ra or rule(h1, 4)
    early = (f1 ^ f1b ^ tau ^ ror(tau, 1)) == 0
    etaok = (eps ^ rol(beta ^ eps, 1)) == etaw
    rz = (r0 == 0) | ((r1 == 0) << 1) | ((r2 == 0) << 2) | ((r3 == 0) << 3)
    hw = sum(bin(x).count('1') for x in (r0, r1, r2, r3))
    ev = ((el >> 1) & 1) << 16 | ((el >> 2) & 1) << 17 | int(ra) << 18 | int(ga) << 19 | int(e3 != 0) << 20 | int(etaok) << 21 \
        | int(early) << 22 | rz << 23
    return dict(d1=d1, T0=T0, a1=a1, y6=y6, y14=y14, h1=h1, tau=tau, eps=eps, psi=psi, eps3=eps3, r0=r0, r1=r1, r2=r2, r3=r3,
                ev=ev, misc=hw | (e3 << 8) | ((el & 0xFFFF) << 16), beta=beta)


def load(path):
    a = np.fromfile(path, dtype=np.uint32)
    return a[:len(a) // RECW * RECW].reshape(-1, RECW)


if __name__ == '__main__':
    R = load(sys.argv[1])
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 3000
    rng = np.random.default_rng(1)
    idx = rng.choice(len(R), size=min(n, len(R)), replace=False)
    # make sure every rare kind is checked if present
    for bit in (16, 32, 64, 128):
        idx = np.union1d(idx, np.nonzero(R[:, 0] & bit)[0][:200])
    bad = 0
    for k in idx:
        r = [int(x) for x in R[k]]
        o = outer([r[F[x]] for x in ('C0d1', 'D2a1', 'D2b1', 'S11', 'S4', 'X9', 'Y4', 'w6')])
        ok = all(o[x] == r[F[x]] for x in o)
        t = trial(r[F['c1']], o)
        ok &= all(t[x] == r[F[x]] for x in ('d1', 'T0', 'a1', 'y6', 'y14', 'h1', 'tau', 'eps', 'psi', 'eps3', 'r0', 'r1', 'r2', 'r3', 'misc'))
        ok &= (r[0] & 0xFFFF0000) == t['ev'] and t['beta'] == BETA_STAR and (r[F['c1']] & CM) == CV
        if not ok:
            bad += 1
            if bad < 5:
                print('MISMATCH record', k, r, o, t)
    print(f'records {len(R)}; checked {len(idx)}; mismatches {bad}')
