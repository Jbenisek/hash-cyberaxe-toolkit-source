
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
for R in 6 5; do bash "${HASHCYBERAXE_WORKSPACE}"/research/blake3_r7/native_probe.sh "${HASHCYBERAXE_WORKSPACE}"/research/blake3_r$R/b8r$R/gen_c/native; echo; done
