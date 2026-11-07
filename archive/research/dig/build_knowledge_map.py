#!/usr/bin/env python3
"""Build D173 cross-hash knowledge summary from the validated cell store."""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "KNOWLEDGE_MAP.md"
CELLS = HERE / "CELLS.jsonl"
HASHES = ["sha256-37", "sha256-38", "sha3-r5", "sha3-r6", "blake3-r2"]


def load():
    return [json.loads(x) for x in CELLS.read_text(encoding="utf-8").splitlines() if x.strip()]


def esc(s):
    return str(s).replace("|", "/").replace("\n", " ")


def top_open(rows):
    a = []
    for x in rows:
        if x["status"] not in ("OPEN", "CLAIMED-UNTESTED"):
            continue
        p, q = x.get("potential_bits"), x.get("prior")
        ev = p*q if isinstance(p, (int,float)) and isinstance(q, (int,float)) else None
        # Missing EV is ranked after numerical EV, but remains blank in the
        # rendered table rather than becoming a fabricated -1 bit value.
        a.append((ev is None, -(ev if ev is not None else 0), ev, x))
    a.sort(key=lambda z: (z[0], z[1]))
    return [(ev, x) for _, _, ev, x in a[:8]]


def main():
    recs = load()
    L = ["# D173 — cross-hash knowledge map", "",
         "Generated from validated `research/dig/CELLS.jsonl` after D170–D172. No search or package build is performed. Status and provenance rules are those in `research/dig/SCHEMA.md`.", "",
         "## Status counts", "",
         "| hash | BEDROCK | COMPUTED | SAMPLED | LOCAL_ONLY | CLAIMED-UNTESTED | KILLED | OPEN | total |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for h in HASHES:
        c = Counter(x["status"] for x in recs if x["hash"] == h)
        L.append("| %s | %d | %d | %d | %d | %d | %d | %d | %d |" %
                 (h, *(c[s] for s in ("BEDROCK","COMPUTED","SAMPLED","LOCAL_ONLY","CLAIMED-UNTESTED","KILLED","OPEN")), sum(c.values())))
    L += ["", "## Per-hash breakdowns", ""]
    static = {
        "sha256-37": {
            "bedrock": "SHA-256 recurrence and the r37 characteristic; exact rows-22–24 reduction (W22/W24 signing, E22 selector, W26 cancellation); dW23=dW25=0 and the inverse E16..E21 construction.",
            "claimed": "Cloud/model claims about per-l row-16 counts, row-16 two-bit closure, hidden W9 closure, dense-family laws, and rank/birthday interpretations remain untested unless a separate own-test record is cited.",
            "open": "Exact row-17/18/19 event interactions; broader dense-family path; full-path necessity of relations not covered by the own tests; r37 rank/freedom claims beyond the proved files.",
            "contr": "EX ratios (exact uniform vs real-pipeline samples), W9 hidden-condition closure, W22 free-bit claims, and rows-25–36 freedom claims have conflicting records; own expansion/audit records kill the fake freedoms.",
            "next": "Prioritize the r37 row-17/18/19 exact carry/event automaton and the dense-family question, keeping the W22/W23 bit-free hold explicitly forbidden."
        },
        "sha256-38": {
            "bedrock": "SHA-256 recurrence and chi38 characteristic; printed E16 head/edrive specification; own expansion audit kills the W23 bits-13/17/26 free claim.",
            "claimed": "Full W23-set gain and Cloud-38 expected EX gain; any outside row-16/17 necessity claim.",
            "open": "Own-law D154 four-pattern measurement, row-16/17 necessity, full W23-set exact count, and full-path tail validation; r38M gamma image claim.",
            "contr": "Measured printed-law EX is +0.161 bit versus the outside ~+1.3-bit expectation; W23-free +4.585 is killed by schedule recomputation; phi-inverse scout is superseded by the measured high-cost solver.",
            "next": "Finish D154 final parse when its handles exit, then treat FP/EX and W23 full-set as separate law-specific questions."
        },
        "sha3-r5": {
            "bedrock": "Keccak-f component recurrence; r5 connector/M4 deterministic structure; exact round-2 cluster count and digest-event exactness in ATLAS_SHA3.",
            "claimed": "No outside SHA3-r5 claim is currently in the cell store.",
            "open": "ANF dependence of 24 FES equations on connector V and the real-value Markov premise; connector relaxation is low-priority because DF is not binding.",
            "contr": "R5 lean score and D/T2 figures differ by ledger/base and overlap; do not add them as independent gains.",
            "next": "Only run the ANF/dependence audit if its bounded ≤0.024-bit ceiling justifies the cost; otherwise leave closed."
        },
        "sha3-r6": {
            "bedrock": "Keccak-f recurrence; event-implied 8-bit distinguished-point filter; derived k=8 optimum and degree-8 XOR-form result.",
            "claimed": "Outside zero-digest closure bounds and any unverified lower-core exclusion.",
            "open": "K=13 memory-rule accounting, DP-rho unit convention, wider-key setup charge, alternative mixed predicates, and rate constants.",
            "contr": "S6K first score is superseded by the F-survivor-mean correction; S6D memory cut is measured slightly worse, not additive.",
            "next": "Resolve the memory-rule and word-width convention before pricing any alternative filter; keep the k=8 cost optimum as the baseline."
        },
        "blake3-r2": {
            "bedrock": "64 G quarter-step construction, Lemma T2 bijection, K2 length cancellation, E0/E2 zero-input structure, and exact E1/E3 outcome partition.",
            "claimed": "G5 tuple-choice claim and any unpriced outside list/stream premise.",
            "open": "Lossless coupled omega-list projection (sampled 71/82), B3M stream/replica memory rule, lambda and rate premises, and G5 parity route.",
            "contr": "G5 early small-sample y claims are killed by the pooled measurement; B3U stack components are additive within measured tolerance but nested stream values must not be added.",
            "next": "Build the phase-resolved coupled omega automaton and price list construction before claiming its sampled ~0.17-bit saving."
        },
    }
    for h in HASHES:
        d = static[h]
        rows = [x for x in recs if x["hash"] == h]
        L += [f"### {h}", "", f"**BEDROCK / COMPUTED foundation.** {d['bedrock']}", "", f"**CLAIMED-UNTESTED.** {d['claimed']}", "", f"**Largest OPEN cells by recorded EV.** {d['open']}", ""]
        L += ["| rank | object | status | EV bits | number | evidence |", "|---:|---|---|---:|---|---|"]
        for n, (ev, x) in enumerate(top_open(rows), 1):
            L.append("| %d | %s | %s | %s | %s | %s |" %
                     (n, esc(x["object"]), x["status"], "" if ev is None else f"{ev:.3f}", esc(x["number"]), esc(x["evidence"])))
        L += ["", f"**Contradictions and reconciliation.** {d['contr']}", "", f"**Next exact action.** {d['next']}", ""]
    topics = defaultdict(list)
    for x in recs:
        if x.get("topic"):
            topics[x["topic"]].append(x)
    L += ["## Cross-hash contradictions", "", "These are the topics with multiple distinct recorded numbers; a contradiction is not automatically an error, because population, law, or accounting may differ.", "", "| topic | hashes | records |", "|---|---|---|"]
    for t in sorted(topics):
        g = topics[t]
        if len({x["number"] for x in g}) <= 1:
            continue
        L.append("| `%s` | %s | %s |" % (t, ", ".join(sorted({x["hash"] for x in g})), "; ".join(f"{x.get('id')}={esc(x['number'])}" for x in g)))
    L += ["", "## Global conclusions", "",
          "1. BEDROCK structure is not the same as a score-bearing lever: every candidate is kept in its own status/provenance class.",
          "2. The strongest proved SHA-256 lever is the r37 exact late-event reduction; r38 deliberately does not inherit it.",
          "3. SHA3 r5/r6 and BLAKE3 currently show no unpriced SHA-style printed-condition gap; their remaining work is cost accounting or exact lossless projection.",
          "4. The highest-EV open cells in the current store are r38 FP, SHA3-r6 memory accounting, r38 full W23 set, BLAKE3 stream, and r37 row-19/20 interactions. None is a submission claim without the cited next test.",
          "", "Source of record: `research/dig/CELLS.jsonl`, `SCHEMA.md`, `GRID_SHA256.md`, `GRID_SHA3.md`, `GRID_BLAKE3.md`, `CONTRADICTIONS.md`, and `OPEN.md`.", ""]
    OUT.write_text("\n".join(L), encoding="utf-8", newline="\n")
    print(f"wrote {OUT} ({len(L)} lines)")


if __name__ == "__main__":
    main()
