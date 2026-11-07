
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
set -e
cd "${HASHCYBERAXE_WORKSPACE}/research/fifties/rates"
export PATH=/usr/local/cuda/bin:$PATH
sed -i '1s/^\xEF\xBB\xBF//' rates.cu
nvcc -O3 -arch=sm_86 -o rates rates.cu
./rates 0 0 8 5 1 t_ord.json t_ord_pass.bin t_ord_sample.bin
./rates 1 0 8 5 1 t_spc.json t_spc_pass.bin t_spc_sample.bin
./rates 2 0 8 5 1 t_spa.json t_spa_pass.bin t_spa_sample.bin
