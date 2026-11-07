#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# stage_r7alg.sh SLOT (WSL): stage the Poseidon r7 algebraic paper package (v2/out) into the NEW slot pos_<slot> (a slot is never reused) (base pos_posgen2), run the organizer intake,
# prefile_check and rulecheck, and write (NOT run) research/launch/submit_pareto_posr7alg.sh. Submits nothing; runs no yukon command.
set -uo pipefail
export PATH="$HOME/.local/bin:$HOME/.bun/bin:$PATH" NO_COLOR=1
W='historical-sources/~~Projects/~HashSmash/workspace'; V="$W/research/poseidon/pkg_r7_paper/v2"; O="$V/pkg"
SLOT="${1:-POSR7ALG2}"; ROOT="$HOME/hashsmash/yukon/pos_$(echo "$SLOT" | tr A-Z a-z)"; ORG="$HOME/hashsmash/yukon/pos_posgen2"; LOG="$V/stage.log"
[ -e "$ROOT" ] && { echo "STOP: slot $ROOT exists"; exit 1; }
: > "$LOG"
mkdir -p "$O/poseidon"
cp -r "$V/out/claim.json" "$V/out/proof.md" "$V/out/experiments" "$V/out/certificates" "$O/poseidon/"; cp "$V/out/submission-note.md" "$O/submission-note.md"
echo "=== slotstage" >> "$LOG"
nice -n 10 bash "$W/research/launch/slotstage/slotstage_pareto.sh" "$SLOT" poseidon 7 "research/poseidon/pkg_r7_paper/v2/pkg/poseidon" "research/poseidon/pkg_r7_paper/v2/pkg/submission-note.md" pos_posgen2 >> "$LOG" 2>&1
echo "=== intake" >> "$LOG"
(cd "$ROOT/pareto" && nice -n 10 python3 -B ../scripts/pareto_pipeline.py --family poseidon intake >> "$LOG" 2>&1); echo "intake rc=$?" >> "$LOG"
echo "=== prefile" >> "$LOG"
PF="$V/pf"; mkdir -p "$PF"; cp -r "$O/poseidon" "$PF/"; cp "$O/submission-note.md" "$PF/"
python3 -B "$W/research/launch/prefile_check.py" "$PF" >> "$LOG" 2>&1
echo "=== rulecheck" >> "$LOG"
RC="$V/rc"; mkdir -p "$RC"; cp -r "$O/poseidon" "$RC/"
python3 -B "$W/research/tools/rulecheck/rulecheck.py" "$RC" >> "$LOG" 2>&1
SRC="$W/research/launch/slotstage/out/submit_$SLOT.sh"; DST="$W/research/launch/submit_pareto_posr7alg.sh"
if [ -f "$SRC" ]; then
  sed -e "s#^\# THE SUBMIT of#\# THE SUBMIT (Poseidon r=7 algebraic paper entry, premise H-GEOM-w2, organizer experiment lowbits-birthday; FILE ONLY AFTER the organizer runner fix and the owner's go) of#" "$SRC" > "$DST"
  python3 -B - "$DST" <<'PYEOF'
import sys
p = sys.argv[1]; s = open(p, newline='').read()
g = '[ -f "${HASHCYBERAXE_WORKSPACE}/research/RUNNER_FIX.flag" ] || { echo "STOP: the organizer runner fix is not flagged (research/RUNNER_FIX.flag missing; the experiment step fails until then). Set FORCE=1 only on the owner word."; [ "${FORCE:-}" = 1 ] || exit 1; }
'
m = 'cd "$DST" || exit 1
'
s = s.replace(m, m + g, 1); open(p, 'w', newline='').write(s)
PYEOF
  chmod +x "$DST"; echo "submit script (NOT run): $DST" >> "$LOG"
fi
echo "done" >> "$LOG"
