"""Write SMT-LIB2 queries: one pinned C3 = G(X3, X7, X11, X15; x_L, W13) whose b and d outputs agree for several
sibling lengths L (all lengths >= 55 share the round-0 state via the K2 trick: a1_L = Q ^ 55 ^ L, x_L = a1_L - K).
Unknowns: T = X3 + X7 - K, Q = K + W4 (the K2 a1 of the 55-byte message), X7, X11, X15, W13 (top byte 0).
C3.a1_L = T + (Q ^ 55 ^ L).
usage: python triple_smt.py L1,L2,L3 out.smt2"""
import sys


def ror(e, r):
    return f"((_ rotate_right {r}) {e})"


def g_bd(a1, B, C, D, y, tag, lines):
    # returns names of b2, d2 for the call with first value a1
    lines.append(f"(define-fun d1{tag} () (_ BitVec 32) {ror(f'(bvxor {D} {a1})', 16)})")
    lines.append(f"(define-fun c1{tag} () (_ BitVec 32) (bvadd {C} d1{tag}))")
    lines.append(f"(define-fun b1{tag} () (_ BitVec 32) {ror(f'(bvxor {B} c1{tag})', 12)})")
    lines.append(f"(define-fun a2{tag} () (_ BitVec 32) (bvadd {a1} b1{tag} {y}))")
    lines.append(f"(define-fun d2{tag} () (_ BitVec 32) {ror(f'(bvxor d1{tag} a2{tag})', 8)})")
    lines.append(f"(define-fun c2{tag} () (_ BitVec 32) (bvadd c1{tag} d2{tag}))")
    lines.append(f"(define-fun b2{tag} () (_ BitVec 32) {ror(f'(bvxor b1{tag} c2{tag})', 7)})")
    return f"b2{tag}", f"d2{tag}"


def main():
    Ls = [int(t) for t in sys.argv[1].split(",")]
    out = sys.argv[2]
    lines = ["(set-logic QF_BV)"]
    for v in ("T", "Q", "B", "C", "D", "Y"):
        lines.append(f"(declare-fun {v} () (_ BitVec 32))")
    lines.append("(assert (= ((_ extract 31 24) Y) #x00))")
    outs = []
    for L in Ls:
        a1 = f"(bvadd T (bvxor Q #x{55 ^ L:08x}))"
        outs.append(g_bd(a1, "B", "C", "D", "Y", f"_{L}", lines))
    for (b, d) in outs[1:]:
        lines.append(f"(assert (= {b} {outs[0][0]}))")
        lines.append(f"(assert (= {d} {outs[0][1]}))")
    lines.append("(check-sat)")
    lines.append("(get-value (T Q B C D Y))")
    open(out, "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
