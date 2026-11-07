
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/shape_any
gcc -O2 -o bd bd.c 2>&1 | head -20
timeout 100 ./bd agg fixed.sys 20 1 > agg_fixed_q.txt 2>&1
head -5 agg_fixed_q.txt
timeout 100 ./bd elim fixed.sys 20 1 > elim_fixed_q.txt 2>&1
head -5 elim_fixed_q.txt
