
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
bash "${HASHCYBERAXE_WORKSPACE}"/research/blake3_r3/pivotv2/stage_run.sh > "${HASHCYBERAXE_WORKSPACE}"/research/blake3_r3/pivotv2/stage_run.out 2>&1
cd "${HASHCYBERAXE_WORKSPACE}"/research/blake3_r3/pivotv2 && python3 -B mk_submit.py > mk_submit.out 2>&1
bash "${HASHCYBERAXE_WORKSPACE}"/research/blake3_r3/pivotv2/rc_run.sh > "${HASHCYBERAXE_WORKSPACE}"/research/blake3_r3/pivotv2/rc_run.out 2>&1
