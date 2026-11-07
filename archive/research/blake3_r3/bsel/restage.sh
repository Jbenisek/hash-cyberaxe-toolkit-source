
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
export PATH="$HOME/.local/bin:$HOME/.bun/bin:$PATH" NO_COLOR=1
P="${HASHCYBERAXE_WORKSPACE}"/research/blake3_r3/compact_u5b/pkg
S=~/hashsmash/yukon/pos_b3r3u5b/pareto
cd $S || exit 1
(cd $P/blake3 && find . -type f -not -path '*/__pycache__/*' -print0) | while IFS= read -r -d '' f; do install -D -m 0644 "$P/blake3/$f" "candidates/blake3/$f"; done
sed -i 's/"submission_state": "draft"/"submission_state": "ready"/' candidates/blake3/claim.json
cp $P/submission-note.md submission-note.md; cp $P/dependencies.json dependencies.json
python3 -B ../scripts/pareto_candidate.py --family blake3 --rounds 3 2>&1 | tail -2
(cd candidates/blake3 && find . -type f -not -path '*/__pycache__/*' -print0 | sort -z | xargs -0 sha256sum) > STAGED.sha256; sha256sum submission-note.md >> STAGED.sha256
rm -rf .yukon/work
nice -n 19 python3 -B ../scripts/pareto_pipeline.py intake --family blake3 2>&1 | tail -2
cat .yukon/work/tracks/blake3-pareto/pareto-outcome.json; echo
cp .yukon/work/tracks/blake3-pareto/experiment-report.json "${HASHCYBERAXE_WORKSPACE}"/research/blake3_r3/compact_u5b/organizer_report_final.json
sha256sum STAGED.sha256 dependencies.json
rm -rf __pycache__ candidates/blake3/__pycache__
