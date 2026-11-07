
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/shape_any
until grep -q "^geo exit" sa_runs.log 2>/dev/null; do sleep 2; done
cp bd2 bd
bash toyshrink.sh > toyshrink.txt 2>&1
echo "toyshrink exit=$? $(date +%T)" >> sa_runs.log
