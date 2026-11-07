
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/dig/incoming2/sha256-38-G04-U05/work
./h1 0 36 7 > out_m0_l36_s7.txt 2>&1
for m in 1 2 3 4 5 6; do ./h1 $m 32 11 > out_m${m}_l32.txt 2>&1; done
./h1 0 32 5 37 > out_m0_l32_steps37.txt 2>&1
