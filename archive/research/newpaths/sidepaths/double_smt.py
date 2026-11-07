"""Two disjoint sibling pairs on one base: C3 (b,d) equal within each pair, e.g. 55-63,57-61.
usage: python double_smt.py 55-63,57-61 out.smt2   (same encoding as triple_smt.py)"""
import sys

from triple_smt import g_bd


def main():
    groups = [[int(t) for t in g.split("-")] for g in sys.argv[1].split(",")]
    out = sys.argv[2]
    lines = ["(set-logic QF_BV)"]
    for v in ("T", "Q", "B", "C", "D", "Y"):
        lines.append(f"(declare-fun {v} () (_ BitVec 32))")
    lines.append("(assert (= ((_ extract 31 24) Y) #x00))")
    for grp in groups:
        outs = []
        for L in grp:
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
