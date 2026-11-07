"""Small derivations used in NATURE.md (no heavy compute)."""
import math

print("1. Neutral-network percolation threshold (Reidys, Stadler, Schuster 1997): lambda* = 1 - a^(-1/(a-1)), a = alphabet size")
for name, a in (("bits (a=2)", 2), ("RNA (a=4)", 4), ("bytes / w=8 words (a=2^8)", 2 ** 8), ("w=32 words (a=2^32)", 2 ** 32)):
    lam = -math.expm1(-math.log(a) / (a - 1))
    print(f"   {name:28s} lambda* = {lam:.4g}  (log2 {math.log2(lam):.2f})")
print("   our neutrality (random-map value, measured 0 hits at the rates below):")
for w in (8, 32):
    print(f"   w={w}: half-digest neutral fraction ~ 2^-{4*w}; strong (E0/E2 inputs) ~ 2^-{8*w}")

print("\n2. Cost of a neutral walk (mutate k words, keep only neutral moves): expected neutral neighbours 2^((k-4)w) for the half")
print("   digest; a step needs about 2^(4w) evaluations whatever k is, i.e. the cost of a fresh half-digest preimage.")
for w in (8, 32):
    print(f"   w={w}: per neutral step ~2^{4*w}; 2^{2*w} members needed for the birthday -> total 2^{6*w} (generic 2^{4*w})")

print("\n3. Catalyst (free tables): a table changes the cost per trial, not the number of trials ('kinetics, not thermodynamics').")
e_ops = (50, 200)
for c in (2, 3, 4, 5):
    L = 32 + 16 * c
    tot = [math.log2(2 * 2 ** L * e / 430 + 2 ** 64 * e / 430) for e in e_ops]
    print(f"   idea 1 with c={c} residual 32-bit checks, two-list join: lists 2^{L}, total 2^{tot[0]:.1f} .. 2^{tot[1]:.1f}")
print("   asymmetric join with one list paid as preprocessing 2^85: other list 2^(192-85)=2^107 -> total >= 2^%.1f" % math.log2(2 ** 107 * 50 / 430))
print("   leaders' path: cost floor 1 op/trial against 1.71 now -> at most %.2f bit (END_OF_LINE 3.1)" % math.log2(1.71))

print("\n4. Random mapping on N = 2^32 points (Flajolet-Odlyzko 1990): image 1-1/e, E[tail]=E[cycle]=sqrt(pi N/8), E[rho]=sqrt(pi N/2)")
N = 2 ** 32
print(f"   image fraction {1 - math.exp(-1):.7f}; sqrt(pi N/8) = {math.sqrt(math.pi * N / 8):.0f}; sqrt(pi N/2) = {math.sqrt(math.pi * N / 2):.0f}")
print("   collision cost of any iterated map f = embed o H is ~1/sqrt(CP(H o embed)); CP excess r lowers it by sqrt(r)")

print("\n5. Codon degeneracy: for fixed A, sum_T n_A(T) = 2^w exactly, so E_T[n] = 1 for every A (degeneracy moves mass, never adds it).")
print("   size-biased (a random member's own T): E[n^2]/E[n] = 1 + Var(n); the extra variants exist only with X held fixed.")
for w in (8, 16, 32):
    rc = 8 * w // 32
    rb = 12 * w // 32
    print(f"   w={w}: (a,c) pivot <= 2^{rc} roots, (b,d) pivot <= 2^{rb}; four columns at once <= 2^{2*rc + 2*rb} relaxed variants per X")
