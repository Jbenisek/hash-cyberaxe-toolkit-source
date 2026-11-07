import json, math
from fractions import Fraction
N = 10377085310562           # reproduced by ledger_I4.py (known answer, time_log2 32.83439)
RATE = 1355
def dT(extra_prim):            # log2 time change for extra primitives
    return math.log2((N + extra_prim) / N)
BLK = 410392 + 87              # shipped block of 2048 steps incl worst prologue
SPACES_ON, SPACES_ALL = 50, 582
E1 = lambda sp, perblock: sp * 8192 * perblock
print("E1 online prim", E1(50, BLK), "share of N", E1(50, BLK)/N, "log2 units", math.log2(E1(50,BLK)/RATE))
print("E1 all-spaces prim", E1(582, BLK), "share", E1(582, BLK)/N)
out = {}
# --- EBUF: block length options (best EP per LB; LB11 = shipped 410,392)
sb = json.load(open("sweepbuf.json"))
rows = []
for LB in (8, 9, 10, 11, 12):
    for EP, (c, nres) in sb[str(LB)].items():
        if LB == 11 and EP == "12": c = 410392
        rows.append((LB, int(EP), nres, c))
def per_space(LB, c): return (1 << (24 - LB)) * (c + 87)
base_ps = per_space(11, 410392)
print("\nLB EP NRES block  prim/step  buffer_bytes  delta_prim_per_space  dT_online  dT_all")
tab = []
for LB, EP, nres, c in rows:
    if EP not in (1, 12, 8): continue
    ps = per_space(LB, c); d = ps - base_ps
    buf = 0 if EP == 1 else 32 * (1 << LB)
    tab.append((LB, EP, nres, c, c/(1<<LB), buf, d, dT(50*d), dT(582*d)))
    print(LB, EP, nres, c, round(c/(1<<LB),2), buf, d, round(dT(50*d),6), round(dT(582*d),6))
json.dump(tab, open("ebuf_table.json", "w"))
# --- EVEC D4 as 24-bit mask rows
def d4_extra_per_block(LB, EP): return (1 << LB) * (EP + 48)    # per step-pass 1 + 3*EW - EW = 1 + 2EW ; passes EP ; EW=24/EP -> EP + 48
x = d4_extra_per_block(11, 12)
dpS = 8192 * x
print("\nD4 as u32 rows: extra per block", x, "per space", dpS, "dT_online", dT(50*dpS), "dT_all", dT(582*dpS))
# 2-prim mask variant (shl + sar) : per step-pass 1 + 2*EW - EW = 1 + EW -> per step EP + 24
x2 = (1 << 11) * (12 + 24); dp2 = 8192 * x2
print("D4 u32 rows, 2-prim mask: extra per block", x2, "dT_online", dT(50*dp2), "dT_all", dT(582*dp2))
# --- EANF streaming
by = {0:1, 1:24, 2:299, 3:2530, 4:16170}
c_in = {w: sum(math.comb(8, j) for j in range(0, 5 - w)) for w in by}
visits = sum(by[w]*c_in[w] for w in by)
stream = visits * 72 + visits * 1
build = 41449*24*3 + 19024*72
print("\nS-visits", visits, "stream prim", stream, "baseline (truth tables + vector XORs)", build, "delta", stream-build)
bound = 1 << 23
other = 617089 + 0
print("2^23 bound", bound, "moebius", 617089, "stream+moebius", stream+617089, "fits", stream + 617089 + 41449*0 <= bound)
# --- bytes
EVEC = (24+276+2024+10626)*768
EANF = 41449*768
G_touched = (1+24+276+2024+10626)*768
A_arr = 41449*4
EBUF_proof, EBUF_code = 32768, 65536
print("\nEVEC", EVEC, "EANF virtual", EANF, "touched", G_touched, "A", A_arr, "D4 bytes", 10626*768, "D4 u32", 10626*4)
MiB = 1 << 20
other_phase = int((0.62 + 2) * MiB)      # D152: one EM 0.62 MiB + code allowance 2 MiB
def S_mem(b): return max(0.0, math.log2(b) - 20)
def phase(anf, evec, buf): return anf + evec + buf + other_phase
opts = {
 "O0 shipped model (ANF virtual 31.8 MB + EVEC + 32 KiB buf)": phase(EANF, EVEC, EBUF_proof),
 "O0b same with code-true 64 KiB buffer": phase(EANF, EVEC, EBUF_code),
 "O1 ANF touched entries only (G 12,951 x 768)": phase(G_touched, EVEC, EBUF_code),
 "O2 ANF freed after setup, loop peak (EVEC+buf)": phase(0, EVEC, EBUF_code),
 "O3 ANF streamed from A (165,796 B) + EVEC": phase(A_arr, EVEC, EBUF_code),
 "O4 O3 + D4 as u32 rows (42,504 B)": phase(A_arr, EVEC - 10626*768 + 10626*4, EBUF_code),
}
print()
for k, b in opts.items():
    print(f"{k:60s} {b:>12,d} B  log2 {math.log2(b):.4f}  S_mem {S_mem(b):.4f}")
cand_phase = 124.12*MiB; Pph = 85.1*MiB; Ephase_dr = 44.65125*MiB
print("candidate phase", cand_phase, math.log2(cand_phase), "P phase", Pph, math.log2(Pph), "E phase (D152)", math.log2(Ephase_dr))
json.dump({k: v for k, v in opts.items()}, open("opts.json", "w"))
