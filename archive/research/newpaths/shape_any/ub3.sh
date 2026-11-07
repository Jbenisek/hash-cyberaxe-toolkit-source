
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/shape_any
# fixed variant with 2 promoted words (F' = 2): promotion search
timeout 600 ./bdp fixed.sys 2 20000 61 m0,m4 > ub_fixed_p2.txt 2>&1
echo "ub_fixed_p2 exit=$? $(date +%T)" >> sa_runs.log
# annealing over elimination orders on the reduced outhalf system (K calls + D0 constant)
timeout 900 ./bd sa outhalf_kmsg.sys 40000 4 62 > sa_outhalf_kmsg.txt 2>&1
echo "sa_outhalf_kmsg exit=$? $(date +%T)" >> sa_runs.log
