
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/tools/traillab
cp traillab /tmp/tl_u02 2>/dev/null
timeout 300 ./traillab backward --chi chi/chi37.txt --rows 15 17 --maxhw 6 --threads 2 > "${HASHCYBERAXE_WORKSPACE}"/research/dig/incoming/sha256-37-U02/work/backward_15_17.txt 2>&1
