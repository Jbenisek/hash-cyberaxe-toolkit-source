"""Depth-2 exchange search for the sets that depth 1 missed (see hold_out_12.txt)."""
import sys, time
from hold import holdable

SETS = [("Y9",), ("Y1",), ("Y4", "w8"), ("Y4", "Y9"), ("Y4", "Y1"), ("Y14", "Y9")]
if __name__ == "__main__":
    for H in SETS:
        t0 = time.time()
        b = holdable(H, depth=2)
        print("%-12s %s  (%.1fs)" % (",".join(H), ("FREE  basis=" + ",".join(b)) if b else "not found (depth 2)",
                                     time.time() - t0))
        sys.stdout.flush()
