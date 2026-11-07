
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
W="${HASHCYBERAXE_WORKSPACE}"/research
bash $W/blake3_r6/b8r6/stage_run.sh > $W/blake3_r6/b8r6/stage_run.out 2>&1
bash $W/blake3_r5/b8r5/stage_run.sh > $W/blake3_r5/b8r5/stage_run.out 2>&1
bash $W/blake3_r6/b8r6/rc_run.sh > $W/blake3_r6/b8r6/rc_run.out 2>&1
bash $W/blake3_r5/b8r5/rc_run.sh > $W/blake3_r5/b8r5/rc_run.out 2>&1
