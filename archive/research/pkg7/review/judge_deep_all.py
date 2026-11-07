#!/usr/bin/env python3
"""Review helper (lens: judge). Reads the raw run files of research/h8/gpu and gpu_more; writes review/judge_deep_all.txt.

The figures of "Real trials against exact expectations" recomputed from the raw files, once for the runs that the
text pools (real40, real42, real45 and layout runs 1..8 = 45 * 2^40 trials) and once for every real run that exists
now (also spread runs 1..8, layout runs 9..24, the 2^45 runs with seeds 8201 and 8202).
"""
import math
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
H8 = HERE.parent.parent / "h8"
exp = (H8 / "gpu" / "out" / "h8_deep_expected.txt").read_text()
m = re.search(r"SUM beta (\S+) bt (\S+) out (\S+) e3 (\S+)", exp)
P = dict(beta=float(m.group(1)), tau=float(m.group(2)), outcome=float(m.group(3)), e3=float(m.group(4)))
out = []


def say(*a):
    out.append(" ".join(str(x) for x in a))


def read(rel):
    p = H8 / rel
    if not p.exists() or p.stat().st_size == 0:
        return None
    t = p.read_text(errors="replace")
    g = lambda pat: re.search(pat, t)
    try:
        return dict(
            trials=2.0 ** float(g(r"STAT \w+ trials 2\^([\d.]+)").group(1)),
            early=int(g(r"early test passes: (\d+)").group(1)),
            e1=int(g(r"E1 requires the eta of Y4: (\d+)").group(1)),
            beta=int(g(r"trials with a listed beta (\d+)").group(1)),
            outcome=int(g(r"trials with a listed E1 outcome (\d+)").group(1)),
            e3=int(g(r"trials with a listed partial E3 event (\d+)").group(1)),
            tau=sum(int(x) for x in re.findall(r"with a listed tau (\d+)", t)),
            rule=int(g(r"rule on h1 .*?passes (\d+)").group(1)))
    except AttributeError:
        return None


sets = {
    "pooled in the text": ["gpu/out/h8_real40.txt", "gpu/out/h8_real42.txt", "gpu/out/h8_real45.txt"] + [f"gpu/out/h8_layout_run{i}.txt" for i in range(1, 9)],
    "independent contexts only, text": ["gpu/out/h8_real40.txt", "gpu/out/h8_real42.txt", "gpu/out/h8_real45.txt"],
    "independent contexts only, all that exist": ["gpu/out/h8_real40.txt", "gpu/out/h8_real42.txt", "gpu/out/h8_real45.txt",
                                                  "gpu_more/out/h8_real45_seed8201.txt", "gpu_more/out/h8_real45_seed8202.txt",
                                                  "gpu_more/out/h8_real45_seed8203.txt"],
    "layout runs 1..24": [f"gpu/out/h8_layout_run{i}.txt" for i in range(1, 9)] + [f"gpu_more/out/h8_layout_run{i}.txt" for i in range(9, 25)],
    "spread runs 1..8": [f"gpu/out/h8_spread_run{i}.txt" for i in range(1, 9)],
}
sets["every real run that exists"] = sorted(set(sets["independent contexts only, all that exist"] + sets["layout runs 1..24"] + sets["spread runs 1..8"]))


def poisson_two_sided(k, mu):
    pk = lambda j: math.exp(-mu + j * math.log(mu) - math.lgamma(j + 1))
    p0 = pk(k)
    return min(1.0, sum(pk(j) for j in range(0, int(mu * 6) + 60) if pk(j) <= p0 * (1 + 1e-12)))


for name, files in sets.items():
    rows = [(f, read(f)) for f in files]
    missing = [f.split("/")[-1] for f, r in rows if r is None]
    rows = [r for _, r in rows if r]
    T = sum(r["trials"] for r in rows)
    line = [f"{name}: {len(rows)} runs, 2^{math.log2(T):.2f} trials" + (f" (no figures: {', '.join(missing)})" if missing else "")]
    for key, label in (("beta", "listed beta"), ("tau", "beta with a listed tau"), ("e3", "listed partial E3 event")):
        k = sum(r[key] for r in rows)
        mu = T * P[key]
        line.append(f"{label} {k:,} against {mu:,.2f} ({(k - mu) / math.sqrt(mu * (1 - P[key])):+.2f})")
    k = sum(r["outcome"] for r in rows)
    mu = T * P["outcome"]
    line.append(f"listed E1 outcome {k} against {mu:.2f} (Poisson two-sided p {poisson_two_sided(k, mu):.3f})")
    k = sum(r["rule"] for r in rows)
    line.append(f"rule 4 on h1 {k:,} against {T / 16:,.0f} ({(k - T / 16) / math.sqrt(T * 15 / 256):+.2f} binomial s.d.)")
    line.append(f"early test {sum(r['early'] for r in rows):,} (2^{math.log2(sum(r['early'] for r in rows) / T):.3f}); "
                f"E1 test {sum(r['e1'] for r in rows):,} (2^{math.log2(sum(r['e1'] for r in rows) / T):.3f})")
    say(" | ".join(line))
sp = [read(f) for f in sets["spread runs 1..8"]]
if all(sp):
    say("spread runs, early test passes: " + " ".join(str(r["early"]) for r in sp) + "; rule 4: " + " ".join(str(r["rule"]) for r in sp))
(HERE / "judge_deep_all.txt").write_text("\n".join(out) + "\n", encoding="utf-8")
print("\n".join(x[:700] for x in out))
