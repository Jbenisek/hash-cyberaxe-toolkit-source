
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}/research/blake3_r4/b4/ext"
python3 -B "${HASHCYBERAXE_WORKSPACE}"/research/tools/memmeter/memmeter.py -- python3 -B gen_only.py ../pkg/blake3/experiments 2>&1 | tail -6
python3 -B "${HASHCYBERAXE_WORKSPACE}"/research/tools/memmeter/memmeter.py -- python3 -B -c "pass" 2>&1 | tail -3
