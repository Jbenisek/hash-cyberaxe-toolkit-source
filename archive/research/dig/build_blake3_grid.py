#!/usr/bin/env python3
"""Build the D172 BLAKE3 two-round quarter-step knowledge grid."""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
WS = HERE.parent.parent
OUT = HERE / "GRID_BLAKE3.md"
CELLS = HERE / "CELLS.jsonl"


def esc(s):
    return str(s).replace("|", "/").replace("\n", " ")


def load_cells():
    out = []
    for line in CELLS.read_text(encoding="utf-8").splitlines():
        if line.strip():
            x = json.loads(line)
            if x["hash"] == "blake3-r2":
                out.append(x)
    return out


def main():
    recs = load_cells()
    lines = [
        "# D172 — BLAKE3 two-round quarter-step knowledge grid", "",
        "Generated from `research/tools/traillab/ATLAS_BLAKE3.md` and validated `research/dig/CELLS.jsonl`; no BLAKE3 search or package build is performed by this generator.", "",
        "## Status discipline", "",
        "`I` is an exactly inverted/solved quarter-step, `P` a pinned/advice value, `0` a proved zero difference, `F` an exact XOR consequence, `$` a paid filter/cube/solver condition, `L` a listed subset of an exact outcome partition, and `Z` a killed door. Evidence status is separate: BEDROCK/COMPUTED/SAMPLED/LOCAL_ONLY/CLAIMED-UNTESTED/KILLED/OPEN.", "",
        "The record has 16 G calls (8 per round), four quarter-steps each: q1=(a1,d1), q2=(c1,b1), q3=(a2,d2), q4=(c2,b2). The table below explicitly expands to all 64 quarter-steps, followed by the output fold.", "",
        "## 64 G quarter-steps", "",
        "| # | round | call | quarter | state terms | construction label | knowledge/effect | evidence |",
        "|---:|---:|---|---|---|---|---|---|"]
    calls = [
        ("K0",0,"I","backward inversion; Lemma T2 bijection"),
        ("K1",0,"I","backward inversion; Lemma T2 bijection"),
        ("K2",0,"I","length difference 55↔63 enters a1; w5 cancellation at a2"),
        ("K3",0,"I","backward inversion; Lemma T2 bijection"),
        ("D0",0,"I","backward inversion; X3 forced pinned constant"),
        ("D1",0,"I","backward inversion; X7 forced pinned constant"),
        ("D2",0,"I","backward inversion; X11 forced pinned constant"),
        ("D3",0,"I","backward inversion; X15 forced pinned constant"),
        ("C0",0,"I","backward from y=Y4 (member)"),
        ("C1",0,"$","forward; Y9=Q filter (1), exact PF prefilter"),
        ("C2",0,"I","forward; Y6,Y14 recomputed per root; certificate"),
        ("C3",0,"P","pinned w4 advice; equal b,d outputs; a,c differ by DY3,DY11"),
        ("E0",1,"0","identical inputs; output fold words 0,2,5,7 contribution equal"),
        ("E1",1,"$","q2 cube Q* fixes beta; q3 listed tau; q4 epsilon/b2 forced"),
        ("E2",1,"0","identical inputs; output fold words 0,2,5,7 contribution equal"),
        ("E3",1,"$","e1 class fixes eta; J1/J2/J3 and solver conditions; all exact consequences of R=0"),
    ]
    quarter_labels = {
        "C1": ["$","$","$","$"], "C2": ["I","I","I","I"], "C3": ["P","P","P","P"],
        "E0": ["0","0","0","0"], "E2": ["0","0","0","0"],
        "E1": ["0","$","L","F"], "E3": ["F","$","F","$"],
    }
    qnames = [("q1","a1,d1"),("q2","c1,b1"),("q3","a2,d2"),("q4","c2,b2")]
    n = 0
    for call, rnd, default, effect in calls:
        labs = quarter_labels.get(call, [default]*4)
        for qi, ((q, terms), lab) in enumerate(zip(qnames, labs), 1):
            n += 1
            lines.append("| %d | %d | %s | %s | `%s` | **%s** | %s | `ATLAS_BLAKE3.md`, pkgB3U proof §§1–10 |" %
                         (n, rnd, call, q, terms, lab, effect))
    lines += ["", "## Output fold", "",
              "| stage | exact dependency | status | evidence |",
              "|---|---|---|---|",
              "| E0/E2 inputs | E0 and E2 have identical inputs; output words 0,2,5,7 are equal | 0 / BEDROCK | ATLAS_BLAKE3.md; CLOSED_DOORS BLAKE3 doors 22,24 |",
              "| residual event | `R=0` is the cross E1/E3 event; outcomes are `(beta,tau,eps)` and partition every R=0 input exactly once | COMPUTED | ATLAS_BLAKE3.md; pkgB3U proof §17 |",
              "| E1/E3 outcome list | listed beta/tau outcomes are a deliberate subset of the exact partition, not a hidden cell/event gap | L / COMPUTED | ATLAS_BLAKE3.md tables A–C |",
              "| final XOR | `o[i]=Z[i] xor Z[i+8]`; digest compare is exact after E1/E3 residual | BEDROCK | ATLAS_BLAKE3.md |",
              "", "## Paid stages and exact counts", "",
              "| stage | count/rate | status | interpretation | evidence |",
              "|---|---|---|---|---|",
              "| filter (1) on Y9 | 14,110,208 / 2^32 | COMPUTED | exact C1/Q prefilter pass | ATLAS_BLAKE3.md; pkgB3U proof §9 |",
              "| typed (2) union | 63,633,856 | COMPUTED | omega projection before coupled checks | ATLAS_BLAKE3.md |",
              "| typed words | 23,820,160 (t=0), 34,028,800 (t=1) | COMPUTED | exact typed list counts | ATLAS_BLAKE3.md |",
              "| listed beta* R=0 mass | 25,165,824 / 71,698,432 = 35.1% | COMPUTED | deliberate listed subset | ATLAS_BLAKE3.md table A |",
              "| listed beta2 R=0 mass | 12,582,912 / 54,005,760 = 23.3% | COMPUTED | deliberate listed subset | ATLAS_BLAKE3.md table A |",
              "| coupled omega removal | 71/82 complete in local sample; 11/82 no joint root | SAMPLED | possible lossless list shrink, not yet counted per phase | ATLAS_BLAKE3.md candidate 1 |",
              "| B3U ledger | 57.18900; five-lever stack; all 15 pairs additive ≤0.0002 | COMPUTED | package record, not a new claim | CELLS B3-B3U |",
              "| B3M stream | S 85.43472 after release; nested with stream and not additive | OPEN | memory-rule/organizer dependency | CELLS B3-STREAM/B3-RELEASE |",
    ]
    lines += ["", "## Closed/open boundaries", "",
              "- No W22-style fake freedom appears: Lemma T2 is a bijection onto admissible blocks.",
              "- Adding unlisted beta outcomes loses at the current ledger because 83% of cost is typed omega-list words; this is the reverse of the SHA-256 printed-cell gap.",
              "- The third-beta row adds zero typed words and has a measured rate gain ceiling around 0.010 bit; it is not a free rate claim.",
              "- The coupled omega list is the main unclosed lossless candidate (sample c=0.866); per-phase exact counting and list-build cost are still required.",
              "- Factor 0.974, lambda, stream/replica memory rules, and G5 alternatives retain their recorded premises/statuses; no outside claim is promoted.",
              "", "## Validated BLAKE3 evidence records", "",
              "| id | status | own test | number | evidence | notes |",
              "|---|---|---|---|---|---|"]
    for x in recs:
        lines.append("| `%s` | %s | %s | %s | %s | %s |" %
                     (x.get("id", ""), x["status"], "yes" if x.get("own_test") else "no",
                      esc(x.get("number", "")), esc(x.get("evidence", "")), esc(x.get("notes", ""))))
    lines += ["", "## D172 conclusion", "",
              "The BLAKE3 two-round record has 64 construction/output quarter-steps represented above. Its only deliberate stricter-than-event choice is the listed outcome set; the exact residual partition itself has no SHA-style hidden multiplicity. The principal remaining mathematical lever is a lossless coupled omega-list projection, presently sampled but not exact or priced.", "",
              "Sources: `research/tools/traillab/ATLAS_BLAKE3.md`, `research/tools/traillab/b3atlas/`, `research/dig/CELLS.jsonl`, and the pkgB3U/B3M proof and ledger records named there.", ""]
    OUT.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print(f"wrote {OUT} ({len(lines)} lines; {n} quarter-steps)")


if __name__ == "__main__":
    main()
