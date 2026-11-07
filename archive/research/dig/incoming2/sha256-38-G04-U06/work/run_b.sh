
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/dig/incoming2/sha256-38-G04-U06/work
gcc -O2 -o absorb absorb.c && ./absorb 20000 > absorb.out; tail -3 absorb.out
cd "${HASHCYBERAXE_WORKSPACE}"/research/dig/incoming2/sha256-38-G04-U06/work/tl
make 2>&1 | grep -i " error" 
gcc -O2 -pthread -o absorb2 absorb2.c src/traillab.c -lm 2>&1 | grep -i error
./traillab check --chi chi/chi38.txt --n 200 --threads 3 > ../check.out 2>&1; tail -12 ../check.out
./absorb2 1000000 | tee ../absorb2.out
