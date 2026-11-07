
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}/research/fifties/av11"
export PATH=/usr/local/cuda/bin:$PATH
nvcc -O3 -arch=sm_86 -o av11_sum av11_sum.cu || exit 1
./av11_sum 00000000 z ${1:-8} 7 11
./av11_sum 80000000 z ${1:-8} 8 11
./av11_sum 00000000 f ${1:-8} 9 11
./av11_sum 80000000 f ${1:-8} 10 11
