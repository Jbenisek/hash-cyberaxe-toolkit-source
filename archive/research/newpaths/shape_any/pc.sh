
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/shape_any/cnf
P=$(pgrep -f "kissat -q r_outhalf_DCEo_T2_S10.cnf" | head -1)
[ -n "$P" ] && kill -STOP $P
for f in pc_kmsg_T6_S0 pc_fixed_T7_S0 pc_outhalf_T6_S10; do
  timeout 300 kissat -q $f.cnf > $f.out 2>&1; echo "$f exit=$? $(date +%T)" >> ../lb_runs.log
done
[ -n "$P" ] && kill -CONT $P
