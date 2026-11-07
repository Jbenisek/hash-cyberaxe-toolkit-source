
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/shape_any
until grep -q "^cutp_fixed_S0" sa_runs.log; do sleep 5; done
cd cnf
timeout 1500 cadical -q r_outhalf_T2_S10.cnf > r_outhalf_T2_S10.cadical.out 2>&1; echo "r_outhalf_T2_S10(cadical) exit=$? $(date +%T)" >> ../lb_runs.log
