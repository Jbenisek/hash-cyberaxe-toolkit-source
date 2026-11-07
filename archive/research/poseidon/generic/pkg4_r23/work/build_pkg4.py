"""Assemble the r = 23 generic package (proof.md, claim.json, submission-note.md) from the parts in this folder and the measurement
summary ../../../orchard/h1meas/summary.json. Checks the intake limits it can check. Usage: python -B build_pkg4.py"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.join(HERE, "..", "poseidon")
MEAS = os.path.join(HERE, "..", "..", "..", "orchard", "h1meas")
S = json.load(open(os.path.join(MEAS, "summary.json")))
plan = json.load(open(os.path.join(HERE, "plan_out.json")))
rho = open(os.path.join(HERE, "rho.py"), encoding="utf-8").read()
cmeas = open(os.path.join(MEAS, "h1meas.c"), encoding="utf-8").read()
head = open(os.path.join(HERE, "proof_head.md"), encoding="utf-8").read()
sec7 = open(os.path.join(HERE, "proof_sec7.md"), encoding="utf-8").read()


def fmt(x, k=3):
    return f"{x:.{k}f}"


# ---- measurement table rows
rows = []
for w in (16, 20, 24, 28, 32, 36, 40):
    a, b, p = S.get(f"A/orch/w{w}"), S.get(f"B/orch/w{w}"), S["pooled"].get(f"orch/w{w}")
    c = S["pooled"].get(f"ctrl/w{w}")
    if not p:
        continue
    succ = "-" if "success_frac" not in p else f'{fmt(a["success_frac"])} / {fmt(b["success_frac"])} ({p["success"]}/{p["K"]}, [{fmt(p["success_ci"][0])}, {fmt(p["success_ci"][1])}])'
    lb = "-" if "lemma_bound" not in p else fmt(p["lemma_bound"], 4)
    rows.append(f'| {w} | {a["K"]} + {b["K"]} | {fmt(a["c_hat"])} / {fmt(b["c_hat"])} | {fmt(p["c_hat"])} [{fmt(p["c_lo"])}, {fmt(p["c_hi"])}] | '
                f'{fmt(c["c_hat"])} [{fmt(c["c_lo"])}, {fmt(c["c_hi"])}] | {succ} | {lb} | {fmt(p["theta_x_mean_gap"])} | '
                f'{fmt(p["theta_x_mean_detection_delay"]) if p["theta_x_mean_detection_delay"] is not None else "-"} | {p.get("max_gap_vs_gmax", "-")} |')
table = ("| w | trials A + B | c run A / run B | c pooled [95%] | control c [95%] | success run A / run B (pooled, [95%]) | Lemma 2 bound | theta x mean DP gap | theta x mean detection delay | largest DP gap / gmax |\n"
         "|---|---|---|---|---|---|---|---|---|---|\n" + "\n".join(rows))
tr = S["trend"]
fx = {w: S["pooled"].get(f"orch0/w{w}") for w in (24, 28, 32)}
cf = {w: (S.get(f"A/ctrlfix/w{w}"), S.get(f"B/ctrlfix/w{w}")) for w in (24, 28)}
vals = dict(TABLE=table, SLOPE=f'{tr["slope_log_c_per_bit"]:+.4f}', SLOPE_SE=f'{tr["se"]:.4f}', CPOOL=fmt(tr["pooled_c_all_widths"]),
            CLO=fmt(S["c_all"]["c_lo"]), CHI=fmt(S["c_all"]["c_hi"]), KALL=S["c_all"]["K"], DT_LO=f'{S["c_all"]["dt_lo"]:.4f}',
            PAIRS=S["pairs"]["pairs"], PAIRS_OK=S["pairs"]["verified_by_organizer_digest"],
            FIX24=fmt(fx[24]["success_frac"]), FIX28=fmt(fx[28]["success_frac"]), FIX32=fmt(fx[32]["success_frac"]),
            CF_SD=fmt(cf[24][0]["sd_success"], 2), CF_SD_B=fmt(cf[24][1]["sd_success"], 2),
            CF_MIN=fmt(min(cf[24][0]["min"], cf[24][1]["min"])), CF_MAX=fmt(max(cf[24][0]["max"], cf[24][1]["max"])),
            B28=f'c = {fmt(S["B/orch/w28"]["c_hat"])} [{fmt(S["B/orch/w28"]["c_lo"])}, {fmt(S["B/orch/w28"]["c_hi"])}]',
            GAPRANGE=f'{fmt(min(S["pooled"][f"orch/w{w}"]["theta_x_mean_gap"] for w in (24, 28, 32, 36, 40)))} to {fmt(max(S["pooled"][f"orch/w{w}"]["theta_x_mean_gap"] for w in (24, 28, 32, 36, 40)))}',
            SUCC_ALL=f'{S["succ_all"]["found"]}/{S["succ_all"]["K"]} = {fmt(S["succ_all"]["frac"])}', SUCC_LB=fmt(S["succ_all"]["bound_mean"], 4),
            MAXEV=f'{S["max_evals"]:,}', MINUTES=S["minutes"])
for k, v in vals.items():
    sec7 = sec7.replace("{{" + k + "}}", str(v))
assert "{{" not in sec7, re.findall(r"\{\{\w+\}\}", sec7)

appA = "## Appendix A: `python3 rho.py --plan`\n\n" + "; ".join(f"{k} {v}" for k, v in plan.items()) + "\n"
appB = ("## Appendix B: the program and its ledger, `rho.py` (verbatim, standard library only; `--plan` prints the parameters and the ledger)\n\n```python\n"
        + rho.rstrip("\n") + "\n```\n")
appC = ("## Appendix C: the measurement program `h1meas.c` (verbatim; links our C Pallas field and Orchard permutation, `pallas.c`)\n\n"
        "Built with `gcc -O2`. Arguments per job: family (o: Orchard digest at r partial rounds; c: control), fixed (0: function index j = seedbase * 1000003 + k, "
        "the rho of trial k), r = 23, w, T, h, S, mcap, gmax (Lemma 2 parameters for N = 2^w, D = T * 2^(w-h), SMAX = 2^(h+3)), trials, seedbase. "
        "Run A used seedbases 1xxxxx, run B 2xxxxx (disjoint functions and starts).\n\n```c\n" + cmeas.rstrip("\n") + "\n```\n")
data = {k: v for k, v in S.items() if k.startswith(("A/", "B/"))}
appD = ("## Appendix D: measurement data (per run, family and width; keys as in Section 7)\n\n```json\n" + json.dumps(data, separators=(",", ":"))
        .replace("},", "},\n") + "\n```\n")
proof = head + sec7 + "\n" + appA + "\n" + appB + "\n" + appC + "\n" + appD
assert "\r" not in proof
os.makedirs(PKG, exist_ok=True)
open(os.path.join(PKG, "proof.md"), "w", encoding="utf-8", newline="\n").write(proof)
L = proof.split("\n")


def sec(title_start):
    """1-based line range of the section whose heading starts with title_start, up to the line before the next ## heading."""
    i = next(k for k, l in enumerate(L) if l.startswith(title_start))
    j = next((k for k in range(i + 1, len(L)) if L[k].startswith("## ")), len(L))
    while L[j - 1].strip() == "":
        j -= 1
    return f"proof:{i + 1}-{j}"


ev_h1 = [sec("## 4."), sec("## 7."), sec("## Appendix C"), sec("## Appendix D")]
claim = json.load(open(os.path.join(HERE, "claim_template.json"), encoding="utf-8"))
for h in claim["heuristics"]:
    if h["id"].startswith("H1"):
        h["evidence_ids"] = ev_h1
    for k in ("statement", "scope", "extrapolation", "limitations"):
        h[k] = h[k]
        for kk, v in vals.items():
            h[k] = h[k].replace("{{" + kk + "}}", str(v))
        assert "{{" not in h[k] and len(h[k]) <= 4096, (h["id"], k, len(h[k]))
for i, r in enumerate(claim["restrictions"]):
    for kk, v in vals.items():
        r = r.replace("{{" + kk + "}}", str(v))
    claim["restrictions"][i] = r
    assert "{{" not in r and len(r) <= 1024, (i, len(r))
open(os.path.join(PKG, "claim.json"), "w", encoding="utf-8", newline="\n").write(json.dumps(claim, indent=1, ensure_ascii=False) + "\n")
note = open(os.path.join(HERE, "note_head.md"), encoding="utf-8").read() + open(os.path.join(HERE, "note_tail.md"), encoding="utf-8").read()
for kk, v in vals.items():
    note = note.replace("{{" + kk + "}}", str(v))
note = note.replace("{{SUMMARY_C}}", S["summary_c"]).replace("{{SUMMARY_S}}", S["summary_s"])
assert "{{" not in note, re.findall(r"\{\{\w+\}\}", note)
open(os.path.join(HERE, "..", "submission-note.md"), "w", encoding="utf-8", newline="\n").write(note)
print(json.dumps({"proof_bytes": len(proof.encode()), "proof_lines": len(L), "note_bytes": len(note.encode()), "evidence_ids": ev_h1,
                  "restriction_max": max(len(r) for r in claim["restrictions"])}))
