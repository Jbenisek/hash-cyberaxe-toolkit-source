
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/poseidon/certb_fast
C=16102098619512022721056163846197557588758949045546201477974792624946581626367
./run_center.sh $C out/l100 --l 100 --check-every 14 --no-abort > out/l100.log
./run_center.sh $C out/l140 --l 140 --check-every 10 --no-abort > out/l140.log
./run_center.sh $C out/l175 --l 175 --check-every 8 --no-abort > out/l175.log
