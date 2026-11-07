
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}/research/fifties/block_neutral/harness"
[ -x ./solve ] || nvcc -O3 -arch=sm_86 -o solve solve.cu 2>&1 | tail -5
/usr/bin/time -f "%e s" ./solve poolG_inst.txt poolG_roots.txt
wc -l poolG_roots.txt
