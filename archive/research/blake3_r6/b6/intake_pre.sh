
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
export PATH="$HOME/.local/bin:$PATH" NO_COLOR=1
W="${HASHCYBERAXE_WORKSPACE}"/research/blake3_r6/b6
S=~/hashsmash/yukon/pos_b3r6pre/pareto
cp $W/pkg/blake3/experiments/bsrho.py $W/pkg/blake3/experiments/manifest.json $S/candidates/blake3/experiments/
cd $S; rm -rf .yukon/work/tracks
date; time nice -n 10 python3 -B ../scripts/pareto_pipeline.py intake --family blake3 2>&1 | tail -3
cat .yukon/work/tracks/blake3-pareto/pareto-outcome.json; echo
cp .yukon/work/tracks/blake3-pareto/experiment-report.json $W/organizer_report.json
rm -rf __pycache__; date
