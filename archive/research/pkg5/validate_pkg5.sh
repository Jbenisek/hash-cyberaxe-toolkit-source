#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# Put the FIFTH blake3-r2 package (research/pkg5/blake3-r2, a draft) into the
# WSL-native clone, in the place of the live candidate, and run the repo's
# mechanical checks there. Research helper, not part of any submission.
# Nothing is submitted and no yukon command is run.
#
# Same as research/validate_track.sh except for where the candidate comes from.
# The mirror is the validation clone ~/hashsmash/hash-smash, not the Yukon checkout; ".yukon/setup.sh" below is the
# test script of the organizer's repository (three unittest runs), not the yukon client.
# The mirror copy of the live candidate is overwritten; the normal script
# restores it the next time it runs. The live folder and the Yukon checkout
# are not touched.
#
#   wsl -d Ubuntu -- bash './research/pkg5/validate_pkg5.sh' [check|tests|intake-ready]...
#
# Everything this script prints is also kept: in research/pkg5/evidence/validation_log.txt when all three steps
# are asked for (tools/pkg5_data.py reads that file for the note's "Checks performed", and uses it only while the
# candidate files have the SHA-256 listed in it), else in evidence/validation_partial_log.txt.
set -euo pipefail

if [ -z "${PKG5_VALIDATE_LOGGED:-}" ]; then
  EVID="${HASHCYBERAXE_WORKSPACE}/research/pkg5/evidence"
  mkdir -p "$EVID"
  case " $* " in *" check "*) c=1;; *) c=0;; esac
  case " $* " in *" tests "*) t=1;; *) t=0;; esac
  case " $* " in *" intake-ready "*) i=1;; *) i=0;; esac
  if [ "$c$t$i" = 111 ]; then LOG="$EVID/validation_log.txt"; else LOG="$EVID/validation_partial_log.txt"; fi
  { echo "validate_pkg5.sh $* ($(date '+%Y-%m-%d %H:%M'))"; PKG5_VALIDATE_LOGGED=1 bash "$0" "$@" 2>&1; echo "exit status $?"; } | tee "$LOG"
  exit "$(tail -1 "$LOG" | sed 's/^exit status //')"
fi

SRC="${HASHCYBERAXE_WORKSPACE}/hash-smash"
PKG="${HASHCYBERAXE_WORKSPACE}/research/pkg5/blake3-r2"
DST="$HOME/hashsmash/hash-smash"
TARGET=blake3-r2
TRACK="$TARGET-exploratory"
CAND="lanes/exploratory/candidates/$TARGET"

if [ ! -d "$DST/.git" ]; then
  mkdir -p "$(dirname "$DST")"
  git clone --quiet "$SRC" "$DST"
fi
cd "$DST"
# Every experiment report of a pkg5 run is kept, named by its own hash, so that
# the pairs of a changed program (another pin or class) can be compared below.
ARCHIVE="$HOME/hashsmash/pkg5-reports"
REPORT="lanes/exploratory/.yukon/work/tracks/$TRACK/experiment-report.json"
mkdir -p "$ARCHIVE"
git fetch --quiet origin
git reset --quiet --hard "$(git -C "$SRC" rev-parse HEAD)"
git clean --quiet -fd -- lanes/exploratory/candidates

rm -rf "$CAND"
mkdir -p "$CAND"
(cd "$PKG" && find . -type f -not -path '*/__pycache__/*' -not -name '*.pyc' -print0) | while IFS= read -r -d '' f; do
  install -D -m 0644 "$PKG/$f" "$CAND/$f"
done
echo "--- candidate files (mirror, from research/pkg5)"
find "$CAND" -type f -printf '%m %6s %p\n' | sort -k3
(cd "$CAND" && find . -type f | sed 's|^\./||' | sort | xargs sha256sum | sed 's/^/sha256 /')
if grep -rlI $'\r' "$CAND" >/dev/null; then
  echo "CRLF line endings found in:"; grep -rlI $'\r' "$CAND"; exit 1
fi
if LC_ALL=C grep -n -P '[^\x00-\x7F]' "$CAND/proof.md" | head -3 | grep -q .; then
  echo "non-ASCII characters in proof.md:"; LC_ALL=C grep -n -P '[^\x00-\x7F]' "$CAND/proof.md" | head -5
fi
left=$(grep -rhoE '\[\[[A-Z0-9_]+\]\]' "$CAND" | sort | uniq -c | tr '\n' ' ' || true)
echo "--- placeholders still in the candidate: ${left:-none}"

for step in "${@:-check}"; do
  case "$step" in
    tests)
      echo "--- .yukon/setup.sh"
      bash .yukon/setup.sh 2>&1 | tail -4
      ;;
    check)
      echo "--- local_tracks.py check $TRACK"
      python3 scripts/local_tracks.py check "$TRACK"
      ;;
    intake-ready)
      # Local dry run of the organizer intake, including the Docker-sandboxed
      # experiments. Drafts skip execution, so only this throwaway mirror copy
      # is flipped to "ready". Nothing is submitted and no AI review runs.
      echo "--- intake with the mirror copy marked ready"
      sed -i 's/"submission_state": "draft"/"submission_state": "ready"/' "$CAND/claim.json"
      python3 scripts/prepare_experiment_image.py --track "$TRACK" 2>&1 | tail -1
      python3 scripts/hashsmash_pipeline.py intake --track "$TRACK"
      cp "$REPORT" "$ARCHIVE/$(sha256sum "$REPORT" | cut -c1-16).json"
      python3 - "$REPORT" "$ARCHIVE" "$(dirname "$PKG")/tools/halfsearch_before_selftest.py" <<'PY'
import glob, hashlib, json, os, subprocess, sys
report = json.load(open(sys.argv[1]))
print("experiment status:", report["status"])
execution = report["execution"] or {}


def programs(e):
    return {s.get("path"): s.get("sha256") for s in e.get("sources", [])}


def pairs(entry):
    return [(r.get("trial"), r.get("message_a_hex"), r.get("message_b_hex")) for r in entry.get("checked_trials", [])]


print("  program sha256:", programs(execution))
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
# the same organizer request answered by an earlier program: are the pairs the same?
done = set()
for path in sorted(glob.glob(os.path.join(sys.argv[2], "*.json"))):
    old = json.load(open(path)).get("execution") or {}
    key = json.dumps(programs(old), sort_keys=True)
    if not old or programs(old) == programs(execution) or key in done:
        continue
    done.add(key)
    for entry in execution.get("experiments", []):
        for other in old.get("experiments", []):
            if other.get("id") == entry.get("id"):
                a, b = pairs(entry), pairs(other)
                print(f"  earlier report, program sha256 {list(programs(old).values())}: {entry.get('id')}: "
                      f"same request {entry.get('request_sha256') == other.get('request_sha256')}, "
                      f"pairs identical in {sum(x == y for x, y in zip(a, b))} of {len(a)} trials")
# The program as it was before the self-test was added (a copy kept by
# a selftest tool; pkg5 has none, so this part is skipped), run here on exactly the organizer's request, which is
# rebuilt from the report and recognised by its hash.
before = sys.argv[3]
if execution and os.path.exists(before):
    def canonical(value):
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode("utf-8")
    print("  program before the self-test: sha256", hashlib.sha256(open(before, "rb").read()).hexdigest())
    material = canonical({"domain": "hashsmash-experiments-v1", "seed": execution.get("seed"),
                          "holdout_nonce": execution.get("holdout_nonce"),
                          "target_config_sha256": execution.get("target_config_sha256")})
    for entry in execution.get("experiments", []):
        if entry.get("kind") != "python-message-pairs-v1":
            continue
        request = {"schema_version": 1, "experiment_id": entry["id"], "target_profile": execution.get("target_profile"),
                   "event": entry["event"], "max_message_bytes": execution.get("organizer_limits", {}).get("max_message_bytes"),
                   "trials": [{"trial": i, "seed": hashlib.sha256(material + canonical([entry["id"], i])).hexdigest()}
                              for i in range(entry["trials"])]}
        rebuilt = hashlib.sha256(canonical(request)).hexdigest() == entry.get("request_sha256")
        out = subprocess.run([sys.executable, "-B", "-s", before], input=canonical(request), capture_output=True, check=True).stdout
        rows = json.loads(out)["trials"]
        a = pairs(entry)
        b = [(r["trial"], r["message_a_hex"], r["message_b_hex"]) for r in rows]
        ta = [r.get("untrusted_participant_observations", {}).get("tries") for r in entry.get("checked_trials", [])]
        tb = [r.get("observations", {}).get("tries") for r in rows]
        print(f"    {entry['id']}: organizer request rebuilt (sha256 equal) {rebuilt}; old program on it: "
              f"pairs identical in {sum(x == y for x, y in zip(a, b))} of {len(a)} trials, tries identical {ta == tb}, "
              f"old stdout sha256 equal to the organizer run's {hashlib.sha256(out).hexdigest() == entry.get('stdout_sha256')}")
PY
      ;;
    *) echo "unknown step: $step"; exit 2 ;;
  esac
done
