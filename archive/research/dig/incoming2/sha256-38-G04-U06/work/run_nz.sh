
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/dig/incoming2/sha256-38-G04-U06/work/tl
export NZ_MAX=4000000 NZ_OUT="${HASHCYBERAXE_WORKSPACE}"/research/dig/incoming2/sha256-38-G04-U06/work/nz_b.bin
timeout 1700 ./traillab window --chi chi/chi38.txt --rows 24 37 --event out --np 24576 --m 256 --mt2 1024 --mw 256 --mt 4096 --seeds 7002 --threads 4 > ../nz_b.out 2>&1
tail -25 ../nz_b.out
