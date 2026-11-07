"""Exact what-if rows for the r38 leader construction (c99df2dc ledger, 0ae69bcb allowances).

Component integers are the c99df2dc exact ledger as rebuilt in
research/grok/work/job65_r38_leader/rebuild.py (D24/D35). Every log2 below is
recomputed here from integers (COMPUTED). Rows whose inputs are op counts we have
not built and counted are marked GUESS in the label; their arithmetic is exact
given the guessed counts.

    python levers_r38.py
"""
from decimal import Decimal, getcontext, ROUND_CEILING
from fractions import Fraction

getcontext().prec = 60
LN2 = Decimal(2).ln()
C = 2728

# c99df2dc ledger components (operations unless noted)
PRE = 466_412_701_031_896_270_852_028          # counted table build + enumeration
INIT = 1024
ONLINE = 11_938_977_653_196_641_712_347_327    # online word ops at the caps
NG = 398_563_284_869_814_990_705               # groups = first blocks
FIN_OPS = 1024
FIN_C = 6

# per-A0-block split at the caps, from proof.md 5.3 / line 641 of the 0ae69bcb dossier
# 30 block + 56.69 entries + 25.41 W7 passes + 4.61 deep + 0.31 prologue/epilogue = 117.0
SPLIT = {"block": Fraction(30), "entries": Fraction(5669, 100), "w7": Fraction(2541, 100),
         "deep": Fraction(461, 100), "pro": Fraction(31, 100)}
PER_BLOCK = sum(SPLIT.values())


def log2(n):
    if isinstance(n, Fraction):
        return (Decimal(n.numerator).ln() - Decimal(n.denominator).ln()) / LN2
    return Decimal(n).ln() / LN2


def ceil5(x):
    s = Decimal(10) ** 5
    return (x * s).to_integral_value(rounding=ROUND_CEILING) / s


def total(ac, a_s, dev, ng_scale=Fraction(1), online_scale=Fraction(1), fb_ops=C):
    """Numerator in operations. ng_scale scales N_G (success-side changes: q3, pair budget, pad).
    online_scale scales the online word ops per group (engine changes). fb_ops replaces the
    C operations charged for each first-block compression (a bit-sliced first block)."""
    ng = NG * ng_scale
    online = Fraction(ONLINE) * ng_scale * online_scale
    num = C * (ac + a_s + dev + FIN_C) + PRE + INIT + FIN_OPS + ng * fb_ops + online
    return num


def show(label, num, base):
    lg = log2(Fraction(num)) - log2(C)
    print(f"{label:<62} {lg:.6f}  ceil5 {ceil5(lg)}  delta {lg - base:+.4f}")
    return lg


A70, A64 = 1 << 70, 1 << 64
base = log2(total(A70, A70, A64)) - log2(C)
print(f"{'leader 0ae69bcb rebuilt (COMPUTED)':<62} {base:.6f}  ceil5 {ceil5(base)}")
attack = log2(total(0, 0, 0) - C * FIN_C) - log2(C)
print(f"attack proper, no allowances (COMPUTED): {attack:.6f}")
print(f"online ops per group (COMPUTED): {Fraction(ONLINE, NG).__float__():.2f}; per A0 block at caps {float(PER_BLOCK):.2f}")
print()
print("# allowance rows (premise changes; arithmetic COMPUTED)")
show("A_S 2^70 -> 2^50 (r37 A_S convention)", total(A70, 1 << 50, A64), base)
show("A_S 2^50 and the 2% N_G pad removed (50/51)", total(A70, 1 << 50, A64, ng_scale=Fraction(50, 51)), base)
show("r37 convention A_C 2^60, A_S 2^50, DEV 2^40", total(1 << 60, 1 << 50, 1 << 40), base)
show("measured-rerun A_C 2^50, A_S 2^50, DEV 2^42 (GUESS inputs)", total(1 << 50, 1 << 50, 1 << 42), base)
print()
print("# success-side rows (H2/H5 margins; arithmetic COMPUTED)")
q3 = Fraction(1, 1)  # placeholder
f_q = Decimal(2) ** Decimal("-0.9899")  # q3 2^-102 -> 2^-101.0101
fq = Fraction(str(f_q))
show("pair budget 1 -> 0.0018 (f = 1/(2-delta))", total(A70, A70, A64, ng_scale=Fraction(10000, 19982)), base)
show("pair budget 1 -> 2^-6 (about 9x measured)", total(A70, A70, A64, ng_scale=1 / (2 - Fraction(1, 64))), base)
show("q3 2^-102 -> 2^-101.0101 (fixed-sample 99% bound)", total(A70, A70, A64, ng_scale=fq), base)
show("both: q3 2^-101.0101 and pair 2^-6", total(A70, A70, A64, ng_scale=fq / (2 - Fraction(1, 64))), base)
show("both, plus A_S 2^50 and no 2% pad", total(A70, 1 << 50, A64, ng_scale=fq / (2 - Fraction(1, 64)) * Fraction(50, 51)), base)
print()
print("# 8bc7d6c5-form premises (its ruling named only H4): q3_model 2^-101.01, structural pair bound")
f_101 = Fraction(str(Decimal(2) ** Decimal("-0.99")))           # 2^-102 -> 2^-101.01
d_struct = Fraction(767, 2 ** 18) + Fraction(191_773_672_732, 2 ** 55)  # 767 x 2^-18 + SR x 2^-55
print(f"  structural delta = {float(d_struct):.6f} (COMPUTED from 8bc7d6c5's H5 constants)")
show("q3_model 2^-102 -> 2^-101.01 (8bc7d6c5 value)", total(A70, A70, A64, ng_scale=f_101), base)
show("pair budget 1 -> structural 0.0029 (8bc7d6c5 form)", total(A70, A70, A64, ng_scale=1 / (2 - d_struct)), base)
show("both 8bc7d6c5-form premises", total(A70, A70, A64, ng_scale=f_101 / (2 - d_struct)), base)
show("both + A_S 2^50 + no 2% pad", total(A70, 1 << 50, A64, ng_scale=f_101 / (2 - d_struct) * Fraction(50, 51)), base)
show("both + A_S 2^50 + no pad + A_C 2^60/DEV 2^40 (r37 convention)", total(1 << 60, 1 << 50, 1 << 40, ng_scale=f_101 / (2 - d_struct) * Fraction(50, 51)), base)
print()
print("# engine rows (op counts are GUESS; arithmetic exact given them)")


def engine(block=None, entries=None, w7=None, deep=None):
    s = dict(SPLIT)
    if block is not None: s["block"] = Fraction(block)
    if entries is not None: s["entries"] = Fraction(entries)
    if w7 is not None: s["w7"] = Fraction(w7)
    if deep is not None: s["deep"] = Fraction(deep)
    return sum(s.values()) / PER_BLOCK


show("first block bit-sliced: 2728 -> 400 ops per group (GUESS)", total(A70, A70, A64, fb_ops=400), base)
show("A0 blocks packed/bit-sliced: 30 -> 15 ops (GUESS)", total(A70, A70, A64, online_scale=engine(block=15)), base)
show("entry loop unrolled, one branch per bucket: 56.69 -> 35 (GUESS)", total(A70, A70, A64, online_scale=engine(entries=35)), base)
show("W7-pass row-17 path bit-sliced per CV: 25.41 -> 15 (GUESS)", total(A70, A70, A64, online_scale=engine(w7=15)), base)
show("N1 cap 4x -> 1.25x (deep 4.61 -> 1.44) (DERIVED)", total(A70, A70, A64, online_scale=engine(deep=Fraction(461, 100) * Fraction(5, 16))), base)
cons = engine(block=15, entries=35, w7=15, deep=Fraction(461, 100) * Fraction(5, 16))
opt = engine(block=12, entries=28, w7=10, deep=Fraction(461, 100) * Fraction(5, 16))
print(f"  engine scale conservative {float(cons):.4f}  optimistic {float(opt):.4f} (per-block ops {float(cons*PER_BLOCK):.1f} / {float(opt*PER_BLOCK):.1f})")
show("engine conservative + first block 400 (GUESS)", total(A70, A70, A64, online_scale=cons, fb_ops=400), base)
show("engine optimistic + first block 250 (GUESS)", total(A70, A70, A64, online_scale=opt, fb_ops=250), base)
show("engine conservative + A_S 2^50 + no pad (GUESS)", total(A70, 1 << 50, A64, ng_scale=Fraction(50, 51), online_scale=cons, fb_ops=400), base)
show("engine cons + margins + A_S 2^50 + no pad (GUESS)", total(A70, 1 << 50, A64, ng_scale=fq / (2 - Fraction(1, 64)) * Fraction(50, 51), online_scale=cons, fb_ops=400), base)
show("engine cons + margins + r37 allowances + no pad (GUESS)", total(1 << 60, 1 << 50, 1 << 40, ng_scale=fq / (2 - Fraction(1, 64)) * Fraction(50, 51), online_scale=cons, fb_ops=400), base)
print()
print("# floor of the construction: attack proper only, per engine setting (GUESS)")
show("attack proper, filed engine (COMPUTED)", total(0, 0, 0) - C * FIN_C, base)
show("attack proper, conservative engine (GUESS)", total(0, 0, 0, online_scale=cons, fb_ops=400) - C * FIN_C, base)
show("attack proper, conservative engine + margins (GUESS)", total(0, 0, 0, ng_scale=fq / (2 - Fraction(1, 64)) * Fraction(50, 51), online_scale=cons, fb_ops=400) - C * FIN_C, base)
