
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/dig/incoming/sha256-37-U02/work
gcc -O3 -march=native -fopenmp -o row15 row15.c || exit 1
OMP_NUM_THREADS=2 ./row15 00fffff0 | head -3
( time OMP_NUM_THREADS=4 timeout 900 ./row15 ffffffff print ) > row15_full.txt 2>&1
