
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
export PATH="$HOME/.local/bin:$HOME/.bun/bin:$PATH" NO_COLOR=1
cd historical-sources/~~Projects/~HashSmash/workspace
nice -n 19 bash research/launch/slotstage/slotstage_pareto.sh B3R7U5B blake3 7 research/blake3_r7/compact_u5b/pkg/blake3 research/blake3_r7/compact_u5b/pkg/submission-note.md pos_b3r4d 2>&1 | tail -8
S=~/hashsmash/yukon/pos_b3r7u5b/pareto
cp research/blake3_r7/compact_u5b/pkg/dependencies.json $S/dependencies.json
cd $S
date; time nice -n 19 python3 -B ../scripts/pareto_pipeline.py intake --family blake3 2>&1 | tail -3
cat .yukon/work/tracks/blake3-pareto/pareto-outcome.json; echo
cp .yukon/work/tracks/blake3-pareto/experiment-report.json "${HASHCYBERAXE_WORKSPACE}/research/blake3_r7/compact_u5b/organizer_report_final.json"
sha256sum STAGED.sha256 dependencies.json
rm -rf __pycache__
date
