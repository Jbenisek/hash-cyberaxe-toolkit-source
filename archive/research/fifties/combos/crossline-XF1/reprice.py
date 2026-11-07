# XF1 reprice with price.py's formula: n = N - 368*A + U_OPEN*A + per_context*K, time_log2 = log2(n/430).
# Every charge in the decision row is a deterministic worst case (DERIVED); measured means are printed for information.

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

import sys, json, math
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/tools/build_pkg/scratch/pkgCJ/work'))
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/fifties/combos/crossline-XF1'))
import frontline_full as F
import walk_mask as X

N, A, K = F.N, F.A_BUDGET + 1, F.RUN_CONTEXTS
base = math.log2(N / 430)
TABLE_FIXED = 20 + 32 * 3 + 64 * 7 + 128 * 6 + 256 * 6 + 512 * 6 + 1024 * 5 + 2048 * 6   # build_table, before entries
TABLE_MAX = TABLE_FIXED + 64 * (2 + 9 + 10) + 64 * 9 * 17                              # every entry at 9 partners
IX_CTX = X.X_IX * F.REP_BATCHES
FB_CTX = X.FALLBACK_MAX * (X.U_FALLBACK - X.U_MASK_WORST)
PER_CTX = TABLE_MAX + IX_CTX + FB_CTX


def row(u_open, per_ctx, once=2 ** 20):
    n = N - F.U_OPEN * A + u_open * A + per_ctx * (K + 1) + once
    return n, math.log2(n / 430)


out = []
p = out.append
p("baseline N %d  time_log2 %.6f  (A = A_BUDGET+1 = %d, K = %d, A/K = %.2f opened per context)" % (N, base, A, K, A / K))
p("charges: U_OPEN_new worst %d (was %d); per context: table max %d + carry index %d (19 x %d rep batches)"
  " + fallback %d (128 x (%d - %d)) = %d; once 2^20 code reserve"
  % (X.U_MASK_WORST, F.U_OPEN, TABLE_MAX, IX_CTX, F.REP_BATCHES, FB_CTX, X.U_FALLBACK, X.U_MASK_WORST, PER_CTX))
n, t = row(X.U_MASK_WORST, PER_CTX)
p("DECISION ROW (worst case): n = %d  time_log2 = %.6f  delta = %+.6f" % (n, t, t - base))
n2, t2 = row(X.U_MASK_WORST - 2 * X.X_CHUNK, PER_CTX)
p("  check, no masked-batch surcharge (X_CHUNK = 0): time_log2 %.6f" % t2)
n3, t3 = row(X.U_MASK_WORST + 40, PER_CTX + 50000)
p("  stress, +40 units per opened cluster and +50000 per context: time_log2 %.6f (delta %+.6f)" % (t3, t3 - base))
# break-even: the per-opened-cluster charge at which delta = -0.10
lo, hi = 0, 368
while hi - lo > 1:
    mid = (lo + hi) // 2
    if row(mid, PER_CTX)[1] <= 63.50:
        lo = mid
    else:
        hi = mid
p("  largest U_OPEN_new that still meets time_log2 <= 63.50 at this per-context charge: %d" % lo)

files = sys.argv[1:]
if files:
    tot, per = {}, []
    for f in files:
        d = json.load(open(f))
        per += d["per_context"]
        X.merge(tot, d["total"])
    nc = len(per)
    p("")
    p("SWEEP: %d contexts (%s)" % (nc, ", ".join(files)))
    for k in ("opened", "closed", "fired_all", "fallback", "fallback_exact", "fired_exact_all", "exact_not_cheap",
              "lost", "mismatch", "prefix_split", "pack_bad", "coref_checked", "coref_bad", "fallback_wouldlose",
              "fallback_wouldmis", "alive9_dead_opened", "e_lanes", "fill_dom_viol"):
        p("  %-20s %d" % (k, tot.get(k, 0)))
    p("  fired_all per context values: %s" % sorted({c["fired_all"] for c in per}))
    p("  chunks per masked cluster, max: %d; table ops max %d (bound %d)" % (
        max(c["chunks_max"] for c in per), max(c["table_ops"] for c in per), TABLE_MAX))
    op = tot["opened"]
    p("  opened per context %.1f; fallback share of opened %.5f; guard-fired clusters per context %.2f" % (
        op / nc, tot["fallback"] / op, tot["fired_all"] / nc))
    p("  units per opened cluster: old %.2f; new mean %.2f (fallback included); new worst charge %d" % (
        tot["units_old"] / op, tot["units_new_mean"] / op, X.U_MASK_WORST))
    p("  survivors per masked cluster: %s; partner survivors: %s" % (tot["surv_hist"], tot["partner_hist"]))
    p("  T2-positive members per opened cluster: %s" % tot["t2_hist"])
    go = [c["fills_old"] for c in per]
    gn = [c["fills_new"] for c in per]
    p("  Y9 fills per context: old layout mean %.2f (min %d, max %d); masked layout mean %.2f (min %d, max %d)" % (
        sum(go) / nc, min(go), max(go), sum(gn) / nc, min(gn), max(gn)))
    p("  premise H_G_cluster 12466 (CM sample mean 208495306067/16777216 = %.2f); masked/premise = %.4f" % (
        208495306067 / 16777216, sum(gn) / nc / 12466))
    p("  contexts with masked fills > old fills: %d" % sum(b > a for a, b in zip(go, gn)))
    um = tot["units_new_mean"] / op
    p("  information row at the measured mean U_OPEN %.2f: time_log2 %.6f" % (um, row(um, PER_CTX)[1]))
    # INFORMATION ONLY (not booked): a separate fill premise for the masked layout, CM's Hoeffding test at delta e^-7
    J = F.REP_BATCHES + 2 * 16384 + 3 * X.FALLBACK_MAX
    mean_g = sum(gn) / nc
    up = mean_g + J * math.sqrt(7 / (2 * nc))
    p("  INFO (not booked): masked range J = %d; Hoeffding e^-7 upper at n = %d: %.1f" % (J, nc, up))
    nD = row(X.U_MASK_WORST, PER_CTX)[0]
    for g in (math.ceil(up), 7000):
        gb = -(-g * K) + J * F._S
        nn = nD - F.U_FILL * (F.G_BUDGET + 1) + F.U_FILL * (gb + 1)
        p("    with H_G_mask <= %d: time_log2 %.6f (needs its own preregistered sample%s)" % (
            g, math.log2(nn / 430), "" if g == math.ceil(up) else "; 7000 is a GUESS target"))
if __name__ == "__main__":
    print("\n".join(out))
    open(_hca_public_path_text('__HCA_WORKSPACE__/research/fifties/combos/crossline-XF1/reprice_out.txt'), "w").write(
        "\n".join(out) + "\n")
