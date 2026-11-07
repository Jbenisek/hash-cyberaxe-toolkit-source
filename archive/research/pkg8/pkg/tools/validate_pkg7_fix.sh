#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# Put the candidate of research/pkg7 (blake3-r2: claim.json, proof.md, certificates/manifest.json,
# experiments/manifest.json and the experiment program experiments/halfsearch.py) into a WSL-native clone of the
# organizer's repository, in the place of the live candidate, and run the repository's mechanical checks there.
# Research helper, not part of any submission. Nothing is submitted, no yukon command is run, nothing is pulled from
# the network: the clone and its fetch read the local checkout, and the experiment image is not pulled (the script
# only asks the local Docker whether the pinned image is there).
#
# Step FIX of 2026-10-06: validate_pkg7_text.sh with its own mirror (hash-smash-pkg7fix) and the same log path; the TEXT step:
# own log (work/text/validation_log.txt), run on the candidate with the text of this package. The state in claim.json is "draft"; only the throwaway copy in the mirror is marked ready, because
# a draft skips the execution of the experiments.
#
# Its own mirror: ~/hashsmash/hash-smash-pkg7fix (the mirrors of the other jobs are not touched).
#
#   wsl -d Ubuntu -- bash "./research/pkg7/tools/validate_pkg7_text.sh" [tests]
#
# With the word tests the unit tests of the repository (.yukon/setup.sh) are run as well. Everything is kept in
# work/text/validation_log.txt; the screen gets the lines that matter.
set -uo pipefail
ROOT="${HASHCYBERAXE_WORKSPACE}/research/pkg8/pkg"
LOG="$ROOT/work/text/validation_log.txt"
if [ -z "${PKG7_VALIDATE_LOGGED:-}" ]; then
  mkdir -p "$ROOT/work/text"
  { echo "validate_pkg7_text.sh $* ($(date '+%Y-%m-%d %H:%M'))"; PKG7_VALIDATE_LOGGED=1 nice -n 5 bash "$0" "$@" 2>&1; echo "exit status $?"; } > "$LOG"
  grep -E '^sha256 .*halfsearch|"status"|^Ran |^OK|^FAILED|experiment status|half-collision:|residual-search:|observation batch_stage|observation batch_lanes|^STOP|^exit status' "$LOG" | cut -c1-200
  exit "$(tail -1 "$LOG" | sed 's/^exit status //')"
fi
set -e
SRC="${HASHCYBERAXE_WORKSPACE}/hash-smash"
BASE="$ROOT/blake3-r2"
DST="$HOME/hashsmash/hash-smash-pkg8"
TARGET=blake3-r2
TRACK="$TARGET-exploratory"
CAND="lanes/exploratory/candidates/$TARGET"

if [ ! -d "$DST/.git" ]; then
  mkdir -p "$(dirname "$DST")"
  git clone --quiet "$SRC" "$DST"
fi
cd "$DST"
ARCHIVE="$HOME/hashsmash/pkg7fix/reports"
REPORT="lanes/exploratory/.yukon/work/tracks/$TRACK/experiment-report.json"
mkdir -p "$ARCHIVE"
git fetch --quiet origin
git reset --quiet --hard "$(git -C "$SRC" rev-parse HEAD)"
git clean --quiet -fd -- lanes/exploratory/candidates
echo "mirror $DST at $(git rev-parse HEAD)"

rm -rf "$CAND"
mkdir -p "$CAND"
(cd "$BASE" && find . -type f -not -path '*/__pycache__/*' -not -name '*.pyc' -print0) | while IFS= read -r -d '' f; do
  install -D -m 0644 "$BASE/$f" "$CAND/$f"
done
echo "--- candidate files (mirror, from research/pkg7/blake3-r2)"
find "$CAND" -type f -printf '%m %6s %p\n' | sort -k3
(cd "$CAND" && find . -type f | sed 's|^\./||' | sort | xargs sha256sum | sed 's/^/sha256 /')
if grep -rlI $'\r' "$CAND" >/dev/null; then
  echo "STOP: CRLF line endings found in:"; grep -rlI $'\r' "$CAND"; exit 1
fi
grep -o '"submission_state": "[a-z]*"' "$CAND/claim.json" | sed 's/^/claim.json as in research\/pkg7: /'

if [ "${1:-}" = tests ]; then
  echo "--- .yukon/setup.sh (the unit tests of the repository)"
  bash .yukon/setup.sh 2>&1 | grep -E '^Ran |^OK|^FAILED|passed' || true
fi

echo "--- local_tracks.py check $TRACK"
python3 scripts/local_tracks.py check "$TRACK"

echo "--- intake with the mirror copy marked ready (no image pull)"
IMAGE=$(python3 -c "from experiments import DEFAULT_DOCKER_IMAGE; print(DEFAULT_DOCKER_IMAGE)")
if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
  echo "STOP: the pinned image $IMAGE is not in the local Docker; nothing was pulled and the experiments were not run"; exit 3
fi
echo "image present locally: $IMAGE"
sed -i 's/"submission_state": "draft"/"submission_state": "ready"/' "$CAND/claim.json"
python3 scripts/hashsmash_pipeline.py intake --track "$TRACK"
cp "$REPORT" "$ARCHIVE/$(sha256sum "$REPORT" | cut -c1-16).json"
python3 - "$REPORT" <<'PY'
import json, sys
report = json.load(open(sys.argv[1]))
print("experiment status:", report["status"])
execution = report["execution"] or {}
print("  program sha256:", {s.get("path"): s.get("sha256") for s in execution.get("sources", [])})
for entry in execution.get("experiments", []):
    rows = entry.get("checked_trials", [])
    seen = [r.get("untrusted_participant_observations", {}) for r in rows]
    obs = [o["tries"] for o in seen if "tries" in o]
    line = (f"  {entry.get('id')}: trials={entry.get('trials')} successes={entry.get('successes')} "
            f"full collisions={sum(bool(r.get('full_collision')) for r in rows)} "
            f"no pair={sum(r.get('reason') == 'no_pair_returned' for r in rows)} "
            f"repeated={sum(bool(r.get('repeated_pair')) for r in rows)} "
            f"replay identical={entry.get('reproducibility', {}).get('stdout_byte_identical')}")
    if obs:
        line += f" tries mean={sum(obs) / len(obs):.1f} max={max(obs)}"
    print(line)
    for key in sorted({k for o in seen for k in o} - {"tries"}):
        values = [o[key] for o in seen if key in o]
        print(f"    observation {key}: {len(values)} rows, values {sorted(set(values))[:8]}, sum {sum(values)}")
PY
