
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
set -e
cd "${HASHCYBERAXE_WORKSPACE}/research/fifties/av11"
export PATH=/usr/local/cuda/bin:$PATH
python3 av11_ref.py
nvcc -O3 -arch=sm_86 -o av11 av11.cu
python3 verify_driver.py 11
python3 verify_driver.py 3
