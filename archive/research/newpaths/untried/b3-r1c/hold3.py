"""Largest free-holdable sets among the E words that are holdable alone (Y9, Y1 are not)."""
import itertools, sys, time
from hold import holdable

W7 = ["Y4", "Y14", "w8", "Y6", "Y12", "w12", "w5"]
if __name__ == "__main__":
    t0 = time.time()
    for r in (3, 4, 5):
        free = []
        for H in itertools.combinations(W7, r):
            b = holdable(H, depth=1)
            if b:
                free.append((H, b))
        print("size %d: %d of %d free-holdable (depth-1 exchange)" % (r, len(free), len(list(itertools.combinations(W7, r)))))
        for H, b in free:
            print("   %-28s basis=%s" % (",".join(H), ",".join(b)))
        sys.stdout.flush()
    print("time %.1fs" % (time.time() - t0))
