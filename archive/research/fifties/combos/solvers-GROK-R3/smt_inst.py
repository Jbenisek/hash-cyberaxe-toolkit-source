"""R3 (Grok, medium confidence): word-level SMT (z3, QF_BV) on one split-point inversion of BITS.md section 1.
Closure G = (C0.a1, C0.b1, C1.a1, D3.a1) as four free 32-bit vars; the 8 split-point coordinates fixed to a real
ctr_outer point (generated as pkg13/mitm/bits/verify.py does: random.Random(seed), rels.point); the other 75 words built
by the triangular reconstruction (core.prop_order) as define-fun terms (bvadd / bvneg / bvxor / rotate_left); the 4
leftover relations asserted as checks.  Variants written:
  inst_true   : free guess words                         (expected sat, exactly 1 solution per BITS.md 5)
  ctl_pinned  : guess words fixed to the true values      (control 1: must be sat at once)
  ctl_bad     : true guess words with bit 0 of C0.a1 flipped, the sttest.py/tocnf.py corruption (control 2: unsat)
  part_bNN    : low NN bits of each guess word free, rest fixed to truth (4*NN free bits; scaling curve)
Also self-tests the term construction in Python against ctr_outer values and the real ctr_outer round-trip.
Usage: python smt_inst.py [seed] [index]   (index = which point of the seeded stream; default seed 99 index 0)"""

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

import sys, os, random, json
BITS = _hca_public_path_text('__HCA_WORKSPACE__/research/pkg13/mitm/bits')
sys.path.insert(0, BITS)
from rels import COORDS, BASIS, point, M, rol, holds, show
from core import CORE, prop_order, mask
import halfsearch as hs   # rels put the experiments dir on sys.path
GUESS = ("C0.a1", "C0.b1", "C1.a1", "D3.a1")
_, ORDER, CHECKS = prop_order(mask(COORDS) | mask(GUESS))
OUT = os.path.dirname(os.path.abspath(__file__))

# tiny expression AST: ("w", name) | ("c", int) | ("neg", e) | ("mul", k, e) | ("add", [e]) | ("xor", [e]) | ("rol", k, e)
def ev(e, v):
    t = e[0]
    if t == "w": return v[e[1]]
    if t == "c": return e[1] & M
    if t == "neg": return (-ev(e[1], v)) & M
    if t == "mul": return (e[1] * ev(e[2], v)) & M
    if t == "add": return sum(ev(x, v) for x in e[1]) & M
    if t == "xor":
        r = 0
        for x in e[1]: r ^= ev(x, v)
        return r
    if t == "rol": return rol(ev(e[2], v), e[1] % 32)
    raise ValueError(t)
def smt(e):
    t = e[0]
    if t == "w": return "|%s|" % e[1]
    if t == "c": return "#x%08x" % (e[1] & M)
    if t == "neg": return "(bvneg %s)" % smt(e[1])
    if t == "mul": return "(bvmul #x%08x %s)" % (e[1] & M, smt(e[2]))
    if t in ("add", "xor"):
        xs = [smt(x) for x in e[1]]
        return xs[0] if len(xs) == 1 else "(%s %s)" % ("bvadd" if t == "add" else "bvxor", " ".join(xs))
    if t == "rol":
        k = e[1] % 32
        return smt(e[2]) if k == 0 else "((_ rotate_left %d) %s)" % (k, smt(e[2]))
    raise ValueError(t)
def scaled(x, c):
    if c == 1: return ("w", x)
    if c == -1: return ("neg", ("w", x))
    return ("mul", c & M, ("w", x))

def definitions():
    'triangular reconstruction: list of (word, expr in earlier words)'
    defs = []
    for i, w in ORDER:
        r = CORE[i]
        if r[0] == "add":
            cw = r[1][w]; assert cw in (1, -1), (w, cw)
            parts = [scaled(x, c) for x, c in r[1].items() if x != w]
            if r[2]: parts.append(("c", r[2]))
            s = ("add", parts)                       # cw*w + s = 0  ->  w = -cw*s
            defs.append((w, ("neg", s) if cw == 1 else s))
        else:
            occ = [rr for xx, rr in r[1] if xx == w]; assert len(occ) == 1, (w, occ)
            parts = [("rol", rr, ("w", xx)) for xx, rr in r[1] if xx != w]
            if r[2]: parts.append(("c", r[2]))
            defs.append((w, ("rol", 32 - occ[0], ("xor", parts))))   # rol(w, rw) = XOR(rest) ^ c
    return defs
def check_exprs():
    out = []
    for i in CHECKS:
        r = CORE[i]
        if r[0] == "add":
            parts = [scaled(x, c) for x, c in r[1].items()] + ([("c", r[2])] if r[2] else [])
            out.append((r[3], ("add", parts)))
        else:
            parts = [("rol", rr, ("w", xx)) for xx, rr in r[1]] + ([("c", r[2])] if r[2] else [])
            out.append((r[3], ("xor", parts)))
    return out

def write(path, v, defs, chks, pin=None, lowfree=None, flip=False):
    L = ["; R3 smt instance: split point fixed, guess words %s" % (", ".join(GUESS)), "(set-logic QF_BV)",
         "(set-option :produce-models true)"]
    for w in COORDS: L.append("(define-fun |%s| () (_ BitVec 32) #x%08x)" % (w, v[w]))
    for g in GUESS: L.append("(declare-const |%s| (_ BitVec 32))" % g)
    for w, e in defs: L.append("(define-fun |%s| () (_ BitVec 32) %s)" % (w, smt(e)))
    for name, e in chks: L.append("(assert (= %s #x00000000)) ; check %s" % (smt(e), name))
    if pin:
        for gi, g in enumerate(GUESS):
            val = v[g] ^ (1 if (flip and gi == 0) else 0)
            L.append("(assert (= |%s| #x%08x))" % (g, val))
    if lowfree is not None:   # fix the top 32-lowfree bits of each guess word to truth
        for g in GUESS:
            L.append("(assert (= ((_ extract 31 %d) |%s|) ((_ extract 31 %d) #x%08x)))" % (lowfree, g, lowfree, v[g]))
    L += ["(check-sat)", "(get-value (%s))" % " ".join("|%s|" % g for g in GUESS)]
    open(path, "w", newline="\n").write("\n".join(L) + "\n")

def make(seed=99, index=0, stem="", parts=(4, 6, 8, 10, 12, 14, 16)):
    rnd = random.Random(seed)
    for _ in range(index + 1): eight, v = point(rnd)
    defs, chks = definitions(), check_exprs()
    # Python self-test of the emitted term structure at the true values
    vv = {w: v[w] for w in list(COORDS) + list(GUESS)}
    for w, e in defs: vv[w] = ev(e, vv)
    det_ok = all(vv[w] == v[w] for w, _ in defs)
    chk_ok = all(ev(e, vv) == 0 for _, e in chks)
    reb = hs.ctr_outer([vv["C0.d1"], vv["D2.a1"], vv["D2.b1"], vv["S11"], vv["S4"], vv["X9"], vv["w6"], eight[7]])
    rt_ok = all(reb[c] == v[c] for c in COORDS if c != "K")
    vb = dict(vv); vb["C0.a1"] ^= 1
    for w, e in defs: vb[w] = ev(e, vb)
    bad_fails = sum(ev(e, vb) != 0 for _, e in chks)
    write(os.path.join(OUT, stem + "inst_true.smt2"), v, defs, chks)
    write(os.path.join(OUT, stem + "ctl_pinned.smt2"), v, defs, chks, pin=True)
    write(os.path.join(OUT, stem + "ctl_bad.smt2"), v, defs, chks, pin=True, flip=True)
    for b in parts: write(os.path.join(OUT, stem + "part_b%02d.smt2" % b), v, defs, chks, lowfree=b)
    info = {"seed": seed, "index": index, "coords": {w: "%08x" % v[w] for w in COORDS},
            "true_guess": {g: "%08x" % v[g] for g in GUESS}, "derived_words": len(defs), "checks": [n for n, _ in chks],
            "selftest": {"terms_reproduce_all_derived_words": det_ok, "four_checks_hold": chk_ok, "ctr_outer_roundtrip": rt_ok,
                         "flipped_guess_failing_checks": bad_fails}}
    json.dump(info, open(os.path.join(OUT, stem + "point.json"), "w"), indent=1)
    return info
if __name__ == "__main__":
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 99; index = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    stem = sys.argv[3] if len(sys.argv) > 3 else ""
    info = make(seed, index, stem)
    print("closure", GUESS, "derived words", info["derived_words"], "checks", info["checks"])
    for i in CHECKS: print("   check", CORE[i][3].ljust(6), show(CORE[i]))
    print("relations", len(CORE), "selftest", info["selftest"])
    print("true guess", info["true_guess"])
