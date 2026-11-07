
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/shape_any
gcc -O2 -o bd bd.c -lm 2>&1 | grep -v -i warn | grep error
timeout 900 ./bd td fixed.sys 12 31 4000 > td_fixed.txt 2>&1
echo "td_fixed exit=$? $(date +%T)" >> sa_runs.log
