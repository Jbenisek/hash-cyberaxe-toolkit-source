
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/shape_any/cnf
pkill -f "kissat -q lb_fixed_k32_T5"
for f in t_fixed_k24_T4 t_fixed_k32_T5; do
  timeout 1500 kissat -q $f.cnf > $f.out 2>&1; echo "$f exit=$? $(date +%T)" >> ../lb_runs.log
done
