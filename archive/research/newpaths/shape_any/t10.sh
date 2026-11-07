
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/shape_any
python3 lbsat6.py outhalf_kmsg.sys 5 0 cnf/s_kmsg_T5_S0.cnf
pkill -f "kissat -q t_outhalf_k32_T2_S10.cnf"
sleep 1
cd cnf
timeout 2400 kissat -q s_kmsg_T5_S0.cnf > s_kmsg_T5_S0.out 2>&1; echo "s_kmsg_T5_S0 exit=$? $(date +%T)" >> ../lb_runs.log
