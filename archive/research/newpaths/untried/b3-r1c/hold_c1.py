"""Are C1's outputs (Y1 -> E1.a, Y9 -> E3.c) free-holdable when t_hi is also free? depth-2 exchange."""
import sys, time
from hold_e import make

if __name__ == "__main__":
    B0 = ["C0.d1", "D2.a1", "D2.b1", "S11", "S4", "X9", "w6", "Y4", "w0", "V13"]
    is_basis, holdable, dof = make(True)
    for H in [("Y9",), ("Y1",), ("Y4", "Y9"), ("Y4", "Y1"), ("Y4", "E1.c1", "w8", "Y9")]:
        t0 = time.time()
        b = holdable(H, B0, depth=2)
        print("t_hi free, hold %-18s %s  (%.0fs)" % (",".join(H), ("FREE basis=" + ",".join(b)) if b else "not found (depth 2)",
                                                    time.time() - t0))
        sys.stdout.flush()
