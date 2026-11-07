
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/shape_any/cnf
for p in $(ps -eo pid,args | grep "pc.sh" | grep -v grep | awk '{print $1}'); do kill $p; done
pkill -f "kissat -q pc_kmsg_T6_S0.cnf"
pkill -CONT -f "r_outhalf_DCEo_T2_S10.cnf"
sleep 1
ps -eo pid,stat,args | grep "[r]_outhalf_DCEo"
start=$(date +%s)
timeout 400 z3 -smt2 z_pc_kmsg_T6_S0.smt2 > z_pc_kmsg_T6_S0.out 2>&1
echo "z_pc_kmsg_T6_S0 exit=$? secs=$(( $(date +%s) - start )) $(date +%T)" >> ../lb_runs.log
head -c 300 z_pc_kmsg_T6_S0.out
