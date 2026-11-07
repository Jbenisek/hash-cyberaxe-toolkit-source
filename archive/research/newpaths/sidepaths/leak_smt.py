"""Which output-difference patterns can one G call produce?  (backs the 'forced structure' argument)

Case K2: inputs (IV2, IV6, IV2, n) with n = 55 vs 63 (XOR 8), message words (x, y) vs (x', y') free.
   For every subset D of {a, b, c, d}: is there an execution pair whose outputs differ EXACTLY on D?
Case IN_<w>: a generic call whose inputs are free but equal except input word w (a, b, c or d), which differs;
   message words free.  Can all four outputs be equal (the difference absorbed inside the call)?
Writes one .smt2 per query into leak/."""
import itertools
import os

os.makedirs("leak", exist_ok=True)
IV2, IV6 = 0x3C6EF372, 0x1F83D9AB


def ror(e, r):
    return f"((_ rotate_right {r}) {e})"


def gcall(p, A, B, C, D, X, Y):
    L = []
    L.append(f"(define-fun {p}a1 () (_ BitVec 32) (bvadd {A} {B} {X}))")
    L.append(f"(define-fun {p}d1 () (_ BitVec 32) {ror(f'(bvxor {D} {p}a1)', 16)})")
    L.append(f"(define-fun {p}c1 () (_ BitVec 32) (bvadd {C} {p}d1))")
    L.append(f"(define-fun {p}b1 () (_ BitVec 32) {ror(f'(bvxor {B} {p}c1)', 12)})")
    L.append(f"(define-fun {p}a2 () (_ BitVec 32) (bvadd {p}a1 {p}b1 {Y}))")
    L.append(f"(define-fun {p}d2 () (_ BitVec 32) {ror(f'(bvxor {p}d1 {p}a2)', 8)})")
    L.append(f"(define-fun {p}c2 () (_ BitVec 32) (bvadd {p}c1 {p}d2))")
    L.append(f"(define-fun {p}b2 () (_ BitVec 32) {ror(f'(bvxor {p}b1 {p}c2)', 7)})")
    return L


def head(vars_):
    return ["(set-logic QF_BV)"] + [f"(declare-fun {v} () (_ BitVec 32))" for v in vars_]


names = []
for r in range(5):
    for D in itertools.combinations("abcd", r):
        L = head(["x", "y", "xp", "yp"])
        L += gcall("P", f"#x{IV2:08x}", f"#x{IV6:08x}", f"#x{IV2:08x}", "#x00000037", "x", "y")
        L += gcall("Q", f"#x{IV2:08x}", f"#x{IV6:08x}", f"#x{IV2:08x}", "#x0000003f", "xp", "yp")
        for o in "abcd":
            op = "distinct" if o in D else "="
            L.append(f"(assert ({op} P{o}2 Q{o}2))")
        L.append("(check-sat)")
        nm = "k2_" + ("".join(D) or "none")
        open(f"leak/{nm}.smt2", "w").write("\n".join(L) + "\n")
        names.append(nm)
for w in "abcd":
    L = head(["a", "b", "c", "d", "ap", "bp", "cp", "dp", "x", "y", "xp", "yp"])
    for o in "abcd":
        L.append(f"(assert ({'distinct' if o == w else '='} {o} {o}p))")
    L += gcall("P", "a", "b", "c", "d", "x", "y")
    L += gcall("Q", "ap", "bp", "cp", "dp", "xp", "yp")
    for o in "abcd":
        L.append(f"(assert (= P{o}2 Q{o}2))")
    L.append("(check-sat)")
    nm = f"in_{w}"
    open(f"leak/{nm}.smt2", "w").write("\n".join(L) + "\n")
    names.append(nm)
open("leak/list.txt", "w").write("\n".join(names) + "\n")
print(len(names), "queries")
