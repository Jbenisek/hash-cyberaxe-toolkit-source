#!/usr/bin/env bash
# stage_paper.sh SLOT (WSL): stage the Poseidon r7 algebraic paper package (v4/out_paper: claim.json, proof.md, certificates/manifest.json, experiments/ (lowbits-birthday), note; no program)
# into the NEW slot pos_<slot> (a slot is never reused) (base pos_posgen2), run the organizer intake, prefile_check and rulecheck, and write (NOT run)
# research/launch/submit_pareto_posr7alg8.sh. Submits nothing; runs no yukon command.
set -uo pipefail
export PATH="$HOME/.local/bin:$HOME/.bun/bin:$PATH" NO_COLOR=1
W='historical-sources/~~Projects/~HashSmash/workspace'; V="$W/research/poseidon/pkg_r7_paper/v4"; O="$V/pkg"
SLOT="${1:-POSR7ALG8}"; ROOT="$HOME/hashsmash/yukon/pos_$(echo "$SLOT" | tr A-Z a-z)"; LOG="$V/stage.log"
[ -e "$ROOT" ] && { echo "STOP: slot $ROOT exists"; exit 1; }
: > "$LOG"
mkdir -p "$O/poseidon"
cp -r "$V/out_paper/claim.json" "$V/out_paper/proof.md" "$V/out_paper/experiments" "$V/out_paper/certificates" "$O/poseidon/"; cp "$V/out_paper/submission-note.md" "$O/submission-note.md"
echo "=== slotstage" >> "$LOG"
nice -n 10 bash "$W/research/launch/slotstage/slotstage_pareto.sh" "$SLOT" poseidon 7 "research/poseidon/pkg_r7_paper/v4/pkg/poseidon" "research/poseidon/pkg_r7_paper/v4/pkg/submission-note.md" pos_posgen2 >> "$LOG" 2>&1
echo "=== intake" >> "$LOG"
(cd "$ROOT/pareto" && nice -n 10 python3 -B ../scripts/pareto_pipeline.py --family poseidon intake >> "$LOG" 2>&1); echo "intake rc=$?" >> "$LOG"
echo "=== prefile" >> "$LOG"
PF="$V/pf"; mkdir -p "$PF"; cp -r "$O/poseidon" "$PF/"; cp "$O/submission-note.md" "$PF/"; cp "$V/dependencies.json" "$PF/"
python3 -B "$W/research/launch/prefile_check.py" "$PF" >> "$LOG" 2>&1
echo "=== rulecheck" >> "$LOG"
RC="$V/rc"; mkdir -p "$RC"; cp -r "$O/poseidon" "$RC/"; cp "$O/submission-note.md" "$RC/"
python3 -B "$W/research/tools/rulecheck/rulecheck.py" "$RC" >> "$LOG" 2>&1
SRC="$W/research/launch/slotstage/out/submit_$SLOT.sh"; DST="$W/research/launch/submit_pareto_$(echo "$SLOT" | tr A-Z a-z).sh"
if [ -f "$SRC" ]; then
  sed -e "s#^\# THE SUBMIT of#\# THE SUBMIT (Poseidon r=7 algebraic paper entry v4 = POSR7ALG8, premise H-GEOM-w2, 256-bit coins, organizer experiment lowbits-birthday, Appendix E; dependencies eed8c9e1; FILE ONLY ON THE OWNER'S GO) of#" "$SRC" > "$DST"
  sed -i "s#--harness \"Claude Code\" --note-file#--harness \"Claude Code\" --dependencies-file \"$V/dependencies.json\" --note-file#" "$DST"
  grep -q -- "--dependencies-file" "$DST" || echo "WARN: dependencies flag not inserted" >> "$LOG"
  chmod +x "$DST"; echo "submit script (NOT run): $DST" >> "$LOG"
fi
echo "done" >> "$LOG"
