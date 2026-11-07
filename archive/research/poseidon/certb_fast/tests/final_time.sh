
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/poseidon/certb_fast
C=$(sed -n 2p tests/centres.txt)
/usr/bin/time -f "wall %e s, user %U s, sys %S s, cpu %P" ./run_center.sh $C out/final > out/final.log 2> out/final.time
nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader
