
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
export PATH="$HOME/.local/bin:$HOME/.bun/bin:$PATH" NO_COLOR=1
cd historical-sources/~~Projects/~HashSmash/workspace
nice -n 19 bash research/launch/slotstage/slotstage_pareto.sh B3R4U5PRE blake3 4 research/blake3_r4/compact/pre/pkg/blake3 research/blake3_r4/compact/pre/pkg/submission-note.md pos_b3r4f2 2>&1 | tail -12
S=~/hashsmash/yukon/pos_b3r4u5pre/pareto
cp research/blake3_r4/compact/pre/pkg/dependencies.json $S/dependencies.json
cd $S
date; time nice -n 19 python3 -B ../scripts/pareto_pipeline.py intake --family blake3 2>&1 | tail -3
cat .yukon/work/tracks/blake3-pareto/pareto-outcome.json; echo
cp .yukon/work/tracks/blake3-pareto/experiment-report.json "${HASHCYBERAXE_WORKSPACE}/research/blake3_r4/compact/organizer_report.json"
rm -rf __pycache__
date
