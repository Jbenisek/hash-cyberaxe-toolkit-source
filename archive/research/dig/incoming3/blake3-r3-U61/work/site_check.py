"""Verify the 16-site formulas used by site_scan.c against the Tracer log (standard state, flags 11 and 10)."""
from b3r3lib import *
def g0(a, b, c, d):
    a = (a + b) & M32; d = ror(d ^ a, 16); c = (c + d) & M32; b = ror(b ^ c, 12)
    a = (a + b) & M32; d = ror(d ^ a, 8); c = (c + d) & M32; b = ror(b ^ c, 7)
    return a, b, c, d
def sites_formula(state):
    p = list(state)
    for j in range(4):
        p[j], p[4 + j], p[8 + j], p[12 + j] = g0(p[j], p[4 + j], p[8 + j], p[12 + j])
    SA, SB, SC, SD = (0, 1, 2, 3), (5, 6, 7, 4), (10, 11, 8, 9), (15, 12, 13, 14)
    out = []
    for k in range(4):
        out += [(p[SA[k]] + p[SB[k]]) & M32, p[SD[k]], p[SC[k]], p[SB[k]]]
    return out
if __name__ == "__main__":
    rng = random.Random(3)
    for trial in range(200):
        st = [rng.getrandbits(32) for _ in range(16)] if trial else init_state()
        tr, per = trace(state=st, log=True)
        nz = [e for e in tr.log if e[0][0] == 0]
        assert len(nz) == 16
        assert [e[2] for e in nz] == sites_formula(st), trial
    print("16-site formulas match the tracer log on 200 states (1 standard + 199 random)")
    st = init_state(); f = sites_formula(st); print("standard sites:", [hex(x) for x in f])
