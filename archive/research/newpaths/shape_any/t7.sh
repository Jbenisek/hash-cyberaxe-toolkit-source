
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/shape_any/cnf
for p in $(ps -eo pid,args | grep "q1.sh" | grep -v grep | awk '{print $1}'); do kill $p; done
pkill -f "kissat -q t_drop_outhalf_D53_S10"
pkill -f "kissat -q --unsat t_fixed_k24_T4"
sleep 1
( timeout 3000 kissat -q r_outhalf_T3_S10.cnf > r_outhalf_T3_S10.out 2>&1; echo "r_outhalf_T3_S10 exit=$? $(date +%T)" >> ../lb_runs.log ) &
( timeout 3000 kissat -q r_outhalf_DCEo_T2_S10.cnf > r_outhalf_DCEo_T2_S10.out 2>&1; echo "r_outhalf_DCEo_T2_S10 exit=$? $(date +%T)" >> ../lb_runs.log ) &
wait
