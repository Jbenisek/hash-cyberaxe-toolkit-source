
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
bash "${HASHCYBERAXE_WORKSPACE}"/research/blake3_r6/b8r6/bld.sh > "${HASHCYBERAXE_WORKSPACE}"/research/blake3_r6/b8r6/bld.out 2>&1 &
bash "${HASHCYBERAXE_WORKSPACE}"/research/blake3_r5/b8r5/bld.sh > "${HASHCYBERAXE_WORKSPACE}"/research/blake3_r5/b8r5/bld.out 2>&1 &
wait
