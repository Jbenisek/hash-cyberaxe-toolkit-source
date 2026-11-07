
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/shape_any/cnf
pkill -f "kissat -q lb3_outhalf_k32_T2_S10"
pkill -f "kissat -q drop_outhalf_D53_S10"
sleep 1
( timeout 3000 kissat -q t_outhalf_k32_T2_S10.cnf > t_outhalf_k32_T2_S10.out 2>&1; echo "t_outhalf_k32_T2_S10 exit=$? $(date +%T)" >> ../lb_runs.log ) &
( timeout 3000 kissat -q --unsat t_fixed_k24_T4.cnf > t_fixed_k24_T4_unsat.out 2>&1; echo "t_fixed_k24_T4(--unsat) exit=$? $(date +%T)" >> ../lb_runs.log ) &
wait
