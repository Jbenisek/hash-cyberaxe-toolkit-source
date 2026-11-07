#!/usr/bin/env python3
"""Build the D171 SHA3-256 r5/r6 component knowledge grid.

Documentation only: no Keccak search is run here. All measured numbers are
read from the validated CELLS store and the local SHA3 atlas.
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
WS = HERE.parent.parent
OUT = HERE / "GRID_SHA3.md"
CELLS = HERE / "CELLS.jsonl"


def cells_for(h):
    ans = []
    for line in CELLS.read_text(encoding="utf-8").splitlines():
        if line.strip():
            x = json.loads(line)
            if x["hash"] == h:
                ans.append(x)
    return ans


def esc(s):
    return str(s).replace("|", "/").replace("\n", " ")


def evidence_table(rows):
    out = ["| id | scope | labels | status | own test | number | evidence | notes |",
           "|---|---|---|---|---|---|---|---|"]
    for x in rows:
        scope = "global" if x.get("row_i") is None and x.get("row_j") is None else f"({x.get('row_i')},{x.get('row_j')})"
        out.append("| `%s` | %s | `%s` | %s | %s | %s | %s | %s |" %
                   (x.get("id", ""), scope, ",".join(x.get("labels") or []), x["status"],
                    "yes" if x.get("own_test") else "no", esc(x.get("number", "")),
                    esc(x.get("evidence", "")), esc(x.get("notes", ""))))
    return out


def main():
    r5 = cells_for("sha3-r5")
    r6 = cells_for("sha3-r6")
    lines = [
        "# D171 — SHA3-256 r5/r6 component knowledge grid", "",
        "Generated from `research/tools/traillab/ATLAS_SHA3.md` and validated `research/dig/CELLS.jsonl`; no Keccak search or package build is performed by this generator.", "",
        "## Status discipline", "",
        "`BEDROCK` is the Keccak-f recurrence/component specification; `COMPUTED` is an exact local calculation; `SAMPLED` is measured with a finite sample; `LOCAL_ONLY` is a window/prefix result; `CLAIMED-UNTESTED` is outside-model material; `KILLED` requires our own evidence; `OPEN` is unresolved. A formula row is not silently promoted to an attack gain.", "",
        "Labels use the D170 alphabet where applicable: `N D X C S I B P K E Z 0`. For SHA3, the component names are `theta`, `rho`, `pi`, `chi`, and `iota`; a component can be BEDROCK while its attack-level lever is OPEN or KILLED.", "",
        "## Keccak-f component map", "",
        "The state is a 5×5 array of 64-bit lanes. Each round is `theta → rho → pi → chi → iota`; theta mixes column parities, rho rotates lanes, pi permutes lane positions, chi is the nonlinear row map, and iota xors the round constant into lane (0,0). The attack rows below name the component at which a printed condition, event, or filter acts.", "",
        "| round | component | r5 (five-round line) | r6 (six-round line) | formula/effect | status | evidence |",
        "|---:|---|---|---|---|---|---|"]
    r5_effect = {}
    def set5(r, c, text, status, evidence="ATLAS_SHA3.md"):
        r5_effect[(r, c)] = (text, status, evidence)
    comps = ("theta", "rho", "pi", "chi", "iota")
    for r in range(6):
        for c in comps:
            set5(r, c, "not in r5" if r == 5 else "Keccak-f component recurrence", "N/A" if r == 5 else "BEDROCK", "r5 has five rounds" if r == 5 else "ATLAS_SHA3.md")
    for c in comps: set5(0, c, "connector fixed bits/linearised transport (no probability loss)", "COMPUTED" if c == "theta" else "BEDROCK")
    for c in comps: set5(1, c, "M4 linear-condition transport; probability 1", "COMPUTED" if c == "theta" else "BEDROCK")
    for c in comps: set5(2, c, "24-equation FES stage-1/event transport", "COMPUTED" if c in ("theta", "rho", "pi") else "BEDROCK")
    set5(2, "chi", "exact cluster test: only the trail contributes", "BEDROCK", "ATLAS_SHA3.md exact cluster count")
    for c in comps: set5(3, c, "no printed conditions; P45 clusters all 2^19 alpha4 values", "BEDROCK")
    for c in comps: set5(4, c, "digest DDT/event path; 4 of 5 bits per plane-0 row", "BEDROCK")
    for r in range(6):
        for c in comps:
            lines.append("| %d | %s | %s | Keccak-f recurrence; no component-local gap established | round recurrence | %s / BEDROCK | %s / ATLAS_SHA3.md |" %
                         (r, c, r5_effect[(r,c)][0], r5_effect[(r,c)][1], r5_effect[(r,c)][2]))
    lines += ["", "## Attack-level rows and exact boundaries", "",
              "| line | printed/control conditions | event requirement | exact or measured result | status | main boundary |",
              "|---|---|---|---|---|---|",
              "| r5 round 0 connector | 520 fixed F bits, E_D zero rows, M2/M3 linearisation | any reachable alpha1 that reaches alpha2 | deterministic in V; DF 33 needed, 45–60 typical | COMPUTED | connector relaxation is not a probability gain; at most 0.21-bit ceiling for whole online part |",
              "| r5 round 1 | 127 M4 linear conditions | alpha2 that reaches a later collision | deterministic by Lemma 2; probability 1 | BEDROCK | no printed/event gap |",
              "| r5 round 2 FES | 24 equations over alpha3 | any alpha3' with nonzero P45 | exact: only the trail among 512 kernel variants; 50 off-kernel changes also zero; 4,000 random alpha3 all zero | COMPUTED | no SHA-256-style cluster gain |",
              "| r5 round 4 digest | DDT rows, 4 of 5 bits per plane-0 row | lanes 0–3 digest equality | event-exact; P45 = 55/2^19 for the trail | COMPUTED | no looser filter gain |",
              "| r6 filter | 8 digest-determined filter bits zero, z=0,1 lanes 0–3 | equal 256-bit digest | event-implied distinguished-point restriction | BEDROCK | value restricted, not an extra event condition |",
              "| r6 key | 140-bit key, 132 free survivor bits | 256-bit collision | proof uses 132 free bits | COMPUTED | wider b and setup charge remain open |",
              "| r6 filter width | k bits | same event | f(k): k=7 21.25, k=8 20.80, k=9 23.77; k=8 optimum | COMPUTED | derived optimum |",
              "| r6 XOR forms | 4 XOR forms per target slice | same event | every tested form degree exactly 8; no cheaper FES | KILLED/COMPUTED | degree-6 shortcut closed |",
              "", "## Open and closed levers", "",
              "| item | status | bound/result | evidence |", "|---|---|---|---|",
              "| r5 dependent FES equations on connector V | OPEN | ceiling 0.024 bit; ANF rank/dependence test not run | ATLAS_SHA3.md ranked gap 1; R5-E1 |",
              "| r5 rounds 3–4 Markov premise | OPEN | affects success, not cost; ceiling small | ATLAS_SHA3.md ranked gap 2 |",
              "| r5 connector relaxation | OPEN/low prior | DF not binding; realistic gain near 0 | ATLAS_SHA3.md ranked gap 3 |",
              "| r6 alternative 8-bit predicates | OPEN | mixed lanes/slices untested; same degree bound expected but not proved | ATLAS_SHA3.md ranked gap 4 |",
              "| r6 key/filter joint charge | OPEN | under 0.01-bit ceiling if kernel already computes z=0,1 cone | ATLAS_SHA3.md ranked gap 5 |",
              "| r6 zero-digest cores below 145 | CLAIMED-UNTESTED | outside-model closure claims only | research/dig/CELLS.jsonl R6-zerodigest |",
              "", "## Validated evidence records", "", "### sha3-r5", ""]
    lines += evidence_table(r5)
    lines += ["", "### sha3-r6", ""]
    lines += evidence_table(r6)
    lines += ["", "## D171 conclusion", "",
              "The strongest supported conclusion is negative: r5’s round-2 cluster is event-exact, and r6’s k=8 filter is already at its derived cost optimum; neither exposes a SHA-256-style printed-condition gap. Remaining candidates are explicitly bounded/open rather than credited. No outside-model statement is promoted to known without an own-test record.", "",
              "Sources: `research/tools/traillab/ATLAS_SHA3.md`, `research/tools/traillab/sha3_atlas/`, `research/dig/CELLS.jsonl`, `research/retest/interaction_grid/wave2_sha3.md`, `research/retest/interaction_grid/wave2_r38.md`, and `research/CLOSED_DOORS.md`.", ""]
    OUT.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print(f"wrote {OUT} ({len(lines)} lines)")


if __name__ == "__main__":
    main()
