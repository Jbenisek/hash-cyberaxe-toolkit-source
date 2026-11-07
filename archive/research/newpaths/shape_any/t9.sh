
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/shape_any
for p in $(ps -eo pid,args | grep "ub2.sh" | grep -v grep | awk '{print $1}'); do kill $p; done
pkill -f "bdp outhalf.sys 2 20000"
sleep 1
cd cnf
timeout 2700 kissat -q s_outhalf_T2_S10.cnf > s_outhalf_T2_S10.out 2>&1; echo "s_outhalf_T2_S10 exit=$? $(date +%T)" >> ../lb_runs.log
