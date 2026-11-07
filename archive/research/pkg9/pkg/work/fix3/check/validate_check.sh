#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# CHECKING agent copy of tools/validate_pkg7_fix.sh: same steps, but its log and report archive are in
# work/fix3/check and its mirror is a fresh throwaway clone under /tmp (the fixing agent's mirror is not touched).
# Nothing is submitted, no yukon command, no network (the clone and fetch read the local checkout; no image pull).
set -uo pipefail
ROOT="${HASHCYBERAXE_WORKSPACE}/research/pkg7"
CHK="$ROOT/work/fix3/check"
LOG="$CHK/validation_log_check.txt"
if [ -z "${PKG7_VALIDATE_LOGGED:-}" ]; then
  { echo "validate_check.sh $* ($(date '+%Y-%m-%d %H:%M'))"; PKG7_VALIDATE_LOGGED=1 nice -n 5 bash "$0" "$@" 2>&1; echo "exit status $?"; } > "$LOG"
  grep -E '"status"|^Ran |^OK|^FAILED|experiment status|half-collision:|residual-search:|^STOP|^exit status' "$LOG" | cut -c1-160 | head -10
  exit 0
fi
set -e
SRC="${HASHCYBERAXE_WORKSPACE}/hash-smash"
BASE="$ROOT/blake3-r2"
DST="/tmp/pkg7check3/hash-smash"
TARGET=blake3-r2
TRACK="$TARGET-exploratory"
CAND="lanes/exploratory/candidates/$TARGET"
if [ ! -d "$DST/.git" ]; then
  mkdir -p "$(dirname "$DST")"
  git clone --quiet "$SRC" "$DST"
fi
cd "$DST"
REPORT="lanes/exploratory/.yukon/work/tracks/$TRACK/experiment-report.json"
git fetch --quiet origin
git reset --quiet --hard "$(git -C "$SRC" rev-parse HEAD)"
git clean --quiet -fd -- lanes/exploratory/candidates
echo "mirror $DST at $(git rev-parse HEAD)"
rm -rf "$CAND"
mkdir -p "$CAND"
(cd "$BASE" && find . -type f -not -path '*/__pycache__/*' -not -name '*.pyc' -print0) | while IFS= read -r -d '' f; do
  install -D -m 0644 "$BASE/$f" "$CAND/$f"
done
(cd "$CAND" && find . -type f | sed 's|^\./||' | sort | xargs sha256sum | sed 's/^/sha256 /')
if grep -rlI $'\r' "$CAND" >/dev/null; then
  echo "STOP: CRLF line endings found in:"; grep -rlI $'\r' "$CAND"; exit 1
fi
grep -o '"submission_state": "[a-z]*"' "$CAND/claim.json" | sed 's/^/claim.json as in research\/pkg7: /'
if [ "${1:-}" = tests ]; then
  echo "--- .yukon/setup.sh (the unit tests of the repository)"
  bash .yukon/setup.sh 2>&1 | grep -E '^Ran |^OK|^FAILED|passed' || true
fi
echo "--- local_tracks.py check $TRACK (draft as in research/pkg7)"
python3 scripts/local_tracks.py check "$TRACK"
echo "--- intake with the mirror copy marked ready (no image pull)"
IMAGE=$(python3 -c "from experiments import DEFAULT_DOCKER_IMAGE; print(DEFAULT_DOCKER_IMAGE)")
if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
  echo "STOP: the pinned image $IMAGE is not in the local Docker; nothing was pulled and the experiments were not run"; exit 3
fi
echo "image present locally: $IMAGE"
sed -i 's/"submission_state": "draft"/"submission_state": "ready"/' "$CAND/claim.json"
grep -o '"submission_state": "[a-z]*"' "$CAND/claim.json" | sed 's/^/claim.json in the mirror copy: /'
echo "--- local_tracks.py check $TRACK (mirror copy marked ready)"
python3 scripts/local_tracks.py check "$TRACK"
python3 scripts/hashsmash_pipeline.py intake --track "$TRACK"
cp "$REPORT" "$CHK/experiment-report-check.json"
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
