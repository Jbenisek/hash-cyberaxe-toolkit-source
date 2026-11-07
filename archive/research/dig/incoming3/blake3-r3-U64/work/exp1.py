import json, random, math
from fractions import Fraction
from eng import *
import rho

def tl2(ops):
    old = rho.PH; rho.PH = ops
    lg = rho.ledger(256); rho.PH = old
    return math.log2(lg["total"] / 638)
R = {}
base = trace(Cfg())[0]; R["base_ops"] = base; R["base_tl2"] = tl2(base)
R["tl2_per_op"] = tl2(base) - tl2(base-1)
R["tl2_hi603"] = tl2(base+8)
rng = random.Random(11)
# B. INIT sensitivity: counter, blen, flags, v8..v11 random / special
def ops_of(**kw):
    return trace(Cfg(**kw), dce=True)[0]
B = {}
B["ctr_random_2000"] = sorted(set(ops_of(ctr=rng.getrandbits(64)) for _ in range(300)))
B["ctr_special"] = {str(c): ops_of(ctr=c) for c in (0, 1, 2, 1023, 1 << 32, (1 << 64) - 1)}
B["blen_all_1_64"] = sorted(set(ops_of(blen=b) for b in range(1, 65)))
B["flags_legal_and_other"] = {str(f): ops_of(flags=f) for f in (1, 2, 3, 4, 8, 10, 11, 12, 13, 14, 15, 16, 32)}
B["v8_11_random"] = sorted(set(ops_of(v8=[rng.getrandbits(32) for _ in range(4)]) for _ in range(100)))
B["cv_random_300"] = sorted(set(ops_of(cv=[rng.getrandbits(32) for _ in range(8)]) for _ in range(300)))
R["B_init"] = B
# validate a few of these configs against the scalar compress
R["B_check"] = all(check_trace(Cfg(ctr=c, blen=b, flags=f, cv=[rng.getrandbits(32) for _ in range(8)])) for c, b, f in ((5, 33, 10), (1 << 40, 64, 12), (0, 1, 1)))
# C. K words
C = {}
for j in range(8):
    C["K%d_nonzero" % j] = ops_of(mconst={j: rng.getrandbits(32) | 1})
C["K_all8_nonzero"] = ops_of(mconst={j: rng.getrandbits(32) | 1 for j in range(8)})
C["K_two_words_col0"] = ops_of(mconst={0: 5, 1: 7})
C["check"] = check_trace(Cfg(mconst={j: rng.getrandbits(32) | 1 for j in range(8)}))
R["C_K"] = C
# D. x placement s = 0..8 (word aligned), x in words s..s+7, rest zero, blen = 4s+32
D = {}
for s in range(0, 9):
    cfg = Cfg(mvar=range(s, s + 8), blen=4 * s + 32)
    D["s%d" % s] = dict(ops=trace(cfg)[0], by=trace(cfg)[1], tl2=tl2(trace(cfg)[0]), blen=4 * s + 32, check=check_trace(cfg))
R["D_place"] = D
# unaligned byte offsets: x begins k bytes into the block, k = 4s+u (u=1..3): words built by shl/and/shr/and/or from raw inputs r0..r7
def unaligned(s, u):
    def mb(tr):
        raw = [("v", "i%d" % i, M32) for i in range(8)]
        m = [("c", 0)] * 16
        sh = 8 * u
        for w in range(9):          # 9 words touched
            lo = raw[w - 1] if w >= 1 else None     # bytes from previous raw word move up
            hi = raw[w] if w < 8 else None
            parts = []
            if lo is not None:     # lo >> (32 - sh)  (low bytes of lo's high part land in low bits)
                a = tr.emit("shr", "%s>>%d" % (lo[1], 32 - sh)); parts.append(a)
            if hi is not None:     # hi << sh masked to 32 bits
                b = tr.emit("shl", "%s<<%d" % (hi[1], sh)); b = tr.emit("and", "%s&%d" % (b, REP * M32)); parts.append(b)
            if len(parts) == 2:
                c = tr.emit("or", "%s|%s" % (parts[0], parts[1]))
            else:
                c = parts[0]
            m[s + w] = ("v", c, M32)
        return m
    return mb
U = {}
for u in (1, 2, 3):
    cfg = Cfg(mvar=[], blen=4 * 7 + u + 32); cfg.mbuilder = unaligned(7, u)
    # input names i0..i7 needed as arguments
    cfg.mvar = []
    ops = trace(cfg, dce=False)[0]
    U["u%d_s7" % u] = ops
R["D_unaligned_lower_bound_ops"] = U
# F. DCE per output
F = {}
for i in range(8):
    F["only_d%d" % i] = trace(Cfg(outs=[i]))[0]
    F["without_d%d" % i] = trace(Cfg(outs=[j for j in range(8) if j != i]))[0]
F["hi_added"] = trace(Cfg(hi=True))[0]
F["hi_only_extra"] = trace(Cfg(hi=True))[0] - base
F["check_hi"] = check_trace(Cfg(hi=True))
R["F_out"] = F
# G. modes
G = {}
op_first_block = trace(Cfg(flags=1))[0]                       # var block, CHUNK_START, non-root (outputs cv words: same 8 xors)
op_root_cvvar = trace(Cfg(cvvar=True, mvar=[], flags=10))[0]  # final block const zeros, cv variable
G["first_var_then_const_last"] = dict(first=op_first_block, last_cvvar=op_root_cvvar, total=op_first_block + op_root_cvvar)
op_mid = trace(Cfg(cv=[rng.getrandbits(32) for _ in range(8)], flags=0))[0]
G["mid_var"] = dict(mid=op_mid, last_cvvar=op_root_cvvar, total=op_mid + op_root_cvvar)
G["last_var_const_prefix"] = trace(Cfg(cv=[rng.getrandbits(32) for _ in range(8)], flags=10))[0]
K8 = {j: rng.getrandbits(32) | 1 for j in range(8)}
par_right = trace(Cfg(flags=12, mconst=K8))[0]                # parent root, left CV const nonzero, right CV var
par_left = trace(Cfg(flags=12, mconst={j: rng.getrandbits(32) | 1 for j in range(8, 16)}, mvar=range(0, 8)))[0]
chunk_t1 = trace(Cfg(ctr=1, flags=3))[0]                      # non-root last chunk (single block), counter 1
G["parent_root_var_right"] = par_right
G["parent_root_var_left"] = par_left
G["chunk_t1_nonroot"] = chunk_t1
G["two_chunk_step"] = chunk_t1 + par_right
G["two_chunk_step_varleft"] = chunk_t1 + par_left
G["three_level_step"] = chunk_t1 + 2 * par_right
G["chain_ok_checks"] = all(check_trace(c) for c in (Cfg(flags=12, mconst=K8), Cfg(flags=12, mconst={j: 3 for j in range(8, 16)}, mvar=range(0, 8)), Cfg(cvvar=True, mvar=[], flags=10)))
G["tl2_two_chunk_step"] = tl2(chunk_t1 + par_right)
R["G_modes"] = G
json.dump(R, open("exp1_out.json", "w"), indent=1)
print(json.dumps(R, indent=1))
