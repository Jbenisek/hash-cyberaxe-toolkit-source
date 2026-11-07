
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/shape_any
for p in $(ps -eo pid,args | grep "t10.sh" | grep -v grep | awk '{print $1}'); do kill $p; done
pkill -f "kissat -q s_kmsg_T5_S0.cnf"
sleep 1
cd cnf
timeout 1700 kissat -q s_fixed_T2_S2.cnf > s_fixed_T2_S2.out 2>&1; echo "s_fixed_T2_S2 exit=$? $(date +%T)" >> ../lb_runs.log
