
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/shape_any
timeout 1200 ./bd catsa fixed.sys 40000 4 21 > catsa_fixed.txt 2>&1
echo "catsa_fixed exit=$?" >> sa_runs.log
timeout 1200 ./bd sa fixed.sys 30000 4 22 > sa2_fixed.txt 2>&1
echo "sa2_fixed exit=$?" >> sa_runs.log
