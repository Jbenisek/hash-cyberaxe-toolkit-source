#!/usr/bin/env bash
# stage_pkg4.sh (WSL): stage the r = 23 generic package (pkg4_r23/poseidon + submission-note.md) into NEW slot pos_posgen4_r23 (base pos_posgen2),
# run the organizer intake, prefile_check and rulecheck (mem-gate), and write (NOT run) research/launch/submit_pareto_posgen4_r23.sh. Submits nothing.
set -uo pipefail
export PATH="$HOME/.local/bin:$HOME/.bun/bin:$PATH" NO_COLOR=1
W='historical-sources/~~Projects/~HashSmash/workspace'; P="$W/research/poseidon/generic/pkg4_r23"; SLOT=POSGEN4_R23; ROOT="$HOME/hashsmash/yukon/pos_posgen4_r23"
LOG="$P/stage.log"; : > "$LOG"
[ -e "$ROOT" ] && { echo "STOP: slot $ROOT exists"; exit 1; }
echo "=== slotstage" | tee -a "$LOG"
nice -n 10 bash "$W/research/launch/slotstage/slotstage_pareto.sh" "$SLOT" poseidon 23 "research/poseidon/generic/pkg4_r23/poseidon" "research/poseidon/generic/pkg4_r23/submission-note.md" pos_posgen2 >> "$LOG" 2>&1
echo "=== intake" | tee -a "$LOG"
(cd "$ROOT/pareto" && nice -n 10 python3 -B ../scripts/pareto_pipeline.py --family poseidon intake >> "$LOG" 2>&1); echo "intake rc=$?" >> "$LOG"
echo "=== prefile" | tee -a "$LOG"
PF="$P/pf"; rm -rf "$PF"; mkdir -p "$PF"; cp -r "$P/poseidon" "$PF/"; cp "$P/submission-note.md" "$PF/"
python3 -B "$W/research/launch/prefile_check.py" "$PF" >> "$LOG" 2>&1
echo "=== rulecheck" | tee -a "$LOG"
RC="$P/rc"; rm -rf "$RC"; mkdir -p "$RC"; cp -r "$P/poseidon" "$RC/"
python3 -B "$W/research/tools/rulecheck/rulecheck.py" "$RC" >> "$LOG" 2>&1
SRC="$W/research/launch/slotstage/out/submit_$SLOT.sh"; DST="$W/research/launch/submit_pareto_posgen4_r23.sh"
if [ -f "$SRC" ]; then sed -e "s#^\# THE SUBMIT of#\# THE SUBMIT (generic rho row r=23, measured-evidence version after eeb5fce5/32a6079d, no dependencies) of#" "$SRC" > "$DST"; chmod +x "$DST"; echo "submit script (NOT run): $DST" | tee -a "$LOG"; fi
grep -E "pareto_candidate rc|\"status\"|intake rc|ALL PASS|SOME FAIL|^FAIL|mem-gate|SUMMARY" "$LOG"
