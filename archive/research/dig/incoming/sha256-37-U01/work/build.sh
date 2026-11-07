
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/dig/incoming/sha256-37-U01/work
gcc -O2 -march=native -w -pthread -o zoneD14 zoneD14.c ../../../../tools/traillab/src/traillab.c ../../../../tools/traillab/src/smc.c ../../../../tools/traillab/src/diff.c -lm 2>&1 | head -30
