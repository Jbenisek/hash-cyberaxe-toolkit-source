
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd ~/hashsmash/yukon
python3 -B "${HASHCYBERAXE_WORKSPACE}/research/blake3_r4/w/cmprep.py" pos_b3r4/pareto/.yukon/work/tracks/blake3-pareto/experiment-report.json pos_b3r4t/pareto/.yukon/work/tracks/blake3-pareto/experiment-report.json
