#!/usr/bin/env python3
"""Build the D170 SHA-256 r37/r38 knowledge grid.

This is a documentation generator.  It reads the two characteristic files,
the validated dig-cell store, and the existing r37 row cards; it performs no
search or cryptographic computation.
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
WS = HERE.parent.parent
CHI = WS / "research" / "tools" / "traillab" / "chi"
CARDS = WS / "research" / "tools" / "traillab" / "row_cards"
CELLS = HERE / "CELLS.jsonl"
OUT = HERE / "GRID_SHA256.md"

STATUS_ORDER = ["KILLED", "BEDROCK", "COMPUTED", "SAMPLED", "LOCAL_ONLY",
                "CLAIMED-UNTESTED", "OPEN"]
STATUS_SHORT = {"KILLED":"K", "BEDROCK":"B", "COMPUTED":"C",
                "SAMPLED":"S", "LOCAL_ONLY":"L", "CLAIMED-UNTESTED":"U",
                "OPEN":"O"}
LABEL_ORDER = list("NDXCSIBPKEZ0")


def parse_chi(path: Path):
    rows = {}
    relations = defaultdict(list)
    text = path.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        m = re.match(r"row\s+(-?\d+)\s+(\S{32})\s+(\S{32})\s+(\S{32})", line)
        if m:
            rows[int(m.group(1))] = {"A": m.group(2), "E": m.group(3), "W": m.group(4)}
        m = re.match(r"x2\s+(.+?)\s*$", line)
        if m:
            rel = m.group(1)
            # A relation is attached to the first row named in it.
            q = re.search(r"(?:A|E|W)(-?\d+)\[", rel)
            if q:
                relations[int(q.group(1))].append(rel)
    return rows, relations, text


def load_cells():
    out = []
    for line in CELLS.read_text(encoding="utf-8").splitlines():
        if line.strip():
            out.append(json.loads(line))
    return out


def parse_card_status(row):
    name = f"row_{row:02d}.md" if row >= 0 else f"row_m{abs(row):02d}.md"
    p = CARDS / name
    if not p.exists():
        return "BEDROCK", "formula only", "No row card present."
    t = p.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"Status:\s*\*\*([^*]+)\*\*\..*?\n", t, re.S)
    status = m.group(1).strip() if m else "BEDROCK"
    m = re.search(r"## Known and open\s*\n\s*KNOWN \(([^)]+)\):\s*(.+?)\n\s*OPEN:", t, re.S)
    if m:
        return status, m.group(1).strip(), " ".join(m.group(2).split())
    return status, "row card", "Formula layer only; no row-specific finite count is attached."


def bit_counts(spec):
    # Character strings are MSB-first; non-'=' symbols are the printed
    # difference/condition positions.  We report counts, not an inferred
    # probability.
    return {k: sum(ch != "=" for ch in spec[k]) for k in ("A", "E", "W")}


def direct_labels(i, j, rmax):
    labels = []
    if i < 0:
        if 0 <= j <= i + 4:
            labels.append("D")
        return labels
    if i <= j <= i + 4 and j <= rmax:
        labels.append("D")
    if i >= 16:
        # W_i is read in the schedule at these four future words.
        for t in (i + 2, i + 7, i + 15, i + 16):
            if t == j and t <= rmax:
                labels.append("X")
    return labels


def best_status(statuses):
    for x in STATUS_ORDER:
        if x in statuses:
            return x
    return "BEDROCK"


def fmt_labels(labels):
    return "".join(x for x in LABEL_ORDER if x in labels) or "N"


def fmt_spec(spec):
    return "A=%s; E=%s; W=%s" % (spec["A"], spec["E"], spec["W"])


def row_formula(r):
    if r < 0:
        return "CV coordinate; no step or W word; consumed by rows %d..%d." % (0, r + 4)
    state = (f"E{r}=S1(E{r-1})+Ch(E{r-1},E{r-2},E{r-3})+E{r-4}+A{r-4}+K{r}+W{r}; "
             f"A{r}=S0(A{r-1})+Maj(A{r-1},A{r-2},A{r-3})+E{r}-A{r-4} (mod 2^32)")
    if r < 16:
        return state + f"; W{r} is a base word."
    return state + f"; W{r}=s1(W{r-2})+W{r-7}+s0(W{r-15})+W{r-16} (mod 2^32)."


def moves(r, rmax):
    if r < 0:
        readers = list(range(0, min(r + 5, rmax + 1)))
        return "state -> rows " + (", ".join(map(str, readers)) if readers else "none")
    state = list(range(r, min(r + 5, rmax + 1)))
    sched = [t for t in (r + 2, r + 7, r + 15, r + 16) if 16 <= t <= rmax] if r >= 16 else []
    a = "state -> rows " + ",".join(map(str, state))
    if sched:
        a += "; schedule -> W" + ",W".join(map(str, sched))
    return a


def r38_row_status(r):
    # Status is deliberately conservative: a characteristic line is a
    # specification, not a full-path proof.
    if r <= 15:
        return "BEDROCK", "chi38 formula/characteristic", "Printed characteristic and recurrence; no independent row-pass count."
    if r == 16:
        return "COMPUTED + OPEN", "S38-phiinv, S38-validset, S38-assign", "Exact 32-word E16 head and inverse/valid-set costs are tested; row-16/17 necessity is still open."
    if r == 17:
        return "OPEN", "S38-bday-time, S38-assign", "Birthday lens is killed, but the row-16/17 local gate assignment has no landed result."
    if 18 <= r <= 22:
        return "BEDROCK + OPEN", "chi38 plus row-interaction audit", "Printed cells and recurrence are fixed; no full-path ablation proves a relaxed condition."
    if r == 23:
        return "SAMPLED + CLAIMED-UNTESTED", "S38-EX, S38-W23set, S38-W23free", "Exact-event sample exists for the printed W23 law; full W23 set is outside-model only and the +3-bit claim is killed."
    if r == 24:
        return "BEDROCK + OPEN", "chi38 formula", "Equal printed state cells are specified; no independent full-path relaxation count."
    if r == 25:
        return "SAMPLED + OPEN", "S38-EX, S38-W25mod-*", "W25 modular event has a local sample; later rows still require recomputed schedule/full-path validation."
    return "OPEN", "chi38 formula", "Equal tail cells are a characteristic prescription, not a proof that the tail is automatic."


def row_freedom(hashname, r):
    if hashname == "r37":
        if r == 15: return "W15=L* (32 values); 28 nonempty row-16 classes, 4 empty."
        if r == 16: return "E16..E21 are six invertible free coordinates; W0..W5 solved by inverse expansion."
        if r == 8: return "W8 back-set: 12,103,680 A0 variants in the cited construction."
        if r in (22, 24, 26): return "No independent late freedom after the exact W22/W24/W26 conditions."
        return "No additional finite freedom/count established."
    if r == 7: return "F7 s0-set in chi38 attack model (outside the row grid; exact size is specified in chi38)."
    if r == 8: return "W8 cell plus three two-bit relations; chi38 records |G|=2^26 in the attack model."
    if r == 16: return "E16 head has exactly 32 listed values; edrive 16..21; inverse solver costs measured separately."
    if r == 23: return "Printed W23 pattern only in local sample; full-set freedom is CLAIMED-UNTESTED."
    return "No independent finite freedom/count established."


def evidence_for_row(recs, h, r):
    got = []
    for x in recs:
        if x["hash"] != h:
            continue
        if x.get("row_i") == r or x.get("row_j") == r:
            got.append(x)
    # Keep every id in the record store available, but make the row table
    # readable by showing a compact status-tagged list.
    return "; ".join(f"{x.get('id')}[{x['status']}]" for x in got) or "none"


def build_matrix(recs, h, lo, hi):
    by = defaultdict(list)
    for x in recs:
        if x["hash"] != h:
            continue
        i, j = x.get("row_i"), x.get("row_j")
        if i is not None and j is not None:
            by[(i, j)].append(x)
    cols = list(range(lo, hi + 1))
    out = []
    out.append("| i\\j | " + " | ".join(map(str, cols)) + " |")
    out.append("|---|" + "---|" * len(cols))
    for i in cols:
        vals = []
        for j in cols:
            labs = set(direct_labels(i, j, hi))
            sts = {"BEDROCK"}
            for x in by.get((i, j), []):
                labs.update(x.get("labels") or [])
                sts.add(x["status"])
            vals.append(f"{fmt_labels(labs)}/{STATUS_SHORT[best_status(sts)]}")
        out.append("| **%d** | %s |" % (i, " | ".join(vals)))
    return out


def evidence_table(recs, h):
    out = ["| id | pair | labels | status | own test | number | evidence | notes |",
            "|---|---|---|---|---|---|---|---|"]
    for x in recs:
        if x["hash"] != h:
            continue
        if x.get("row_i") is None and x.get("row_j") is None:
            pair = "global"
        else:
            pair = f"({x.get('row_i')},{x.get('row_j')})"
        ev = x.get("evidence", "").replace("|", "/").replace("\n", " ")
        no = x.get("notes", "").replace("|", "/").replace("\n", " ")
        # Older dig records store numeric values directly; normalize them for
        # the Markdown table instead of assuming every `number` is text.
        num = str(x.get("number", "")).replace("|", "/").replace("\n", " ")
        out.append("| `%s` | %s | `%s` | %s | %s | %s | %s | %s |" %
                   (x.get("id", ""), pair, ",".join(x.get("labels") or []), x["status"],
                    "yes" if x.get("own_test") else "no", num, ev, no))
    return out


def main():
    r37, rel37, t37 = parse_chi(CHI / "chi37.txt")
    r38, rel38, t38 = parse_chi(CHI / "chi38.txt")
    recs = load_cells()
    lines = []
    lines += ["# D170 — SHA-256 r37/r38 full knowledge grid", "",
              "Generated from `chi37.txt`, `chi38.txt`, the r37 row cards, and validated `research/dig/CELLS.jsonl`; no search or cryptographic run is performed by this generator.",
              "", "## Status discipline", "",
              "`BEDROCK` means recurrence/characteristic structure or an exhaustive proof in a cited file; `COMPUTED` means an exact local computation; `SAMPLED` means a measured estimate; `LOCAL_ONLY` is window/prefix-only; `CLAIMED-UNTESTED` is outside-model material; `KILLED` requires our own file; `OPEN` has no result. A characteristic cell is not silently promoted to a full-path collision proof.",
              "", "Labels are `N D X C S I B P K E Z 0`: neutral, direct state, direct schedule, carry, selector, invertible, branching, parity collapse, killed freedom, exact event, tested no gain, proved constant. `x`/transitive schedule dependence is described in the row and move columns rather than used as a store label.",
              "", "## Common SHA-256 row equations", "",
              "For every step `r >= 0`, `E_r = S1(E_{r-1}) + Ch(E_{r-1},E_{r-2},E_{r-3}) + E_{r-4} + A_{r-4} + K_r + W_r` and `A_r = S0(A_{r-1}) + Maj(A_{r-1},A_{r-2},A_{r-3}) + E_r - A_{r-4}` modulo `2^32`. For `r < 16`, `W_r` is a base word; for `r >= 16`, `W_r = s1(W_{r-2}) + W_{r-7} + s0(W_{r-15}) + W_{r-16}`. Rows `-4..-1` are chaining-value coordinates.",
              "", "## Difference support and schedule facts", "",
              "r37’s parsed support is `A={6,7,10,11,12,13,14,16}`, `E={6,7,8,9,10,11,12,13,14,15,17,18,20}`, `W={6,7,8,9,10,14,15,22,24}`. The exact r37 schedule conclusions are: `dW16=0`, `dW17=0`, `dW18=dW19=dW20=0`, `dW21=0`, `dW22` is the nonzero schedule-forced branch, `dW23=0`, `dW24` is nonzero, `dW25=0`, `dW26` must cancel, and `dW27..dW36=0` once that cancellation holds. Evidence: `research/tools/traillab/ATLAS37.md`, `research/retest/rows22_24/RESULT.md`, `research/retest/r16_per_l/RESULT.md`.",
              "", "r38’s printed support is listed row-by-row below. Its characteristic file specifies the equal tail, but no r38 analogue of the r37 rows-22–24 automatic-tail proof is assumed; every r38 tail statement remains conditional/open unless a cited r38 file proves it.",
              ""]

    for title, h, rows, rel, lo, hi, rstatus in (("SHA-256 r37 (37 steps)", "sha256-37", r37, rel37, -4, 36, None),
                                                  ("SHA-256 r38 (38 steps)", "sha256-38", r38, rel38, -4, 37, r38_row_status)):
        lines += [f"## {title}", "",
                  "Columns: printed A/E/W strings are MSB-first; `neq` is the count of non-`=` symbols, not an inferred probability. `rank` is the known closing rank only where the source supplies one. `evidence IDs` point into CELLS.jsonl and therefore preserve own-test versus outside provenance.", "",
                  "| row | status | inputs/formula | printed cells (neq A/E/W) | two-bit relations | rank | freedom | what moves | evidence IDs |",
                  "|---:|---|---|---|---|---:|---|---|---|"]
        rank = {16:17,17:13,18:15,19:6,20:7,21:1,22:11,24:4} if h == "sha256-37" else {}
        for row in range(lo, hi + 1):
            spec = rows.get(row, {"A":"="*32, "E":"="*32, "W":"="*32})
            if h == "sha256-37":
                st, cite, note = parse_card_status(row)
            else:
                st, cite, note = rstatus(row)
            c = bit_counts(spec)
            rels = "; ".join(rel.get(row, [])) or "none"
            printed = f"A `{spec['A']}` / E `{spec['E']}` / W `{spec['W']}`; neq {c['A']}/{c['E']}/{c['W']}"
            lines.append("| %d | %s | %s | %s | %s | %s | %s | %s | %s |" %
                         (row, st, row_formula(row).replace("|", "/"), printed, rels,
                          rank.get(row, "—"), row_freedom("r37" if h == "sha256-37" else "r38", row),
                          moves(row, hi), evidence_for_row(recs, h, row)))
        lines += ["", "### Pair interaction matrix", "",
                  "Each token is `LABELS/STATUS`; formula-derived N/D/X cells are BEDROCK (`/B`). Additional letters and a stronger evidence status are overlaid from CELLS.jsonl. Thus an OPEN exact-event question can appear as e.g. `DX/O` without erasing the proved recurrence dependency.", ""]
        lines += build_matrix(recs, h, lo, hi)
        lines += ["", "### Recorded pair/global evidence", ""]
        lines += evidence_table(recs, h)
        lines += ["", "### Interpretation limits", "",
                  "The matrix is a dependency/knowledge map, not a multiplication of marginal probabilities. For r37, the exact late reduction and the killed W22/W23-free-bit artifact are proved only by the files named above. For r38, the local EX/W25 samples and solver costs do not establish the untested full-set W23 lever, row-16/17 necessity, or an automatic tail.", ""]

    lines += ["## D170 audit summary", "",
              "- r37 rows `-4..36`: all 41 rows are represented with recurrence, printed cells, relations, rank/freedom, moves, and evidence IDs. The rank vector is `17,13,15,6,7,1,11` for rows 16..22 and `4` for row 24; zero elsewhere.",
              "- r38 rows `-4..37`: all 42 rows are represented. The chi38 file supplies the 38-step characteristic and 32-value E16 head; no r37 late-tail proof is imported into r38.",
              "- Outside material under `row_interactions/` is represented only through `CLAIMED-UNTESTED` CELLS records unless an own-test record confirms it.",
              "- Main open cells remain r37 row-17/18/19 exact-event interactions and r38 row-16/17 necessity, full W23-set, and full-path tail validation.",
              "", "Source paths: `research/tools/traillab/chi/chi37.txt`, `research/tools/traillab/chi/chi38.txt`, `research/tools/traillab/ATLAS37.md`, `research/tools/traillab/row_cards/`, `research/dig/CELLS.jsonl`, and `row_interactions/` (read as data only).", ""]
    OUT.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print(f"wrote {OUT} ({len(lines)} lines)")


if __name__ == "__main__":
    main()
