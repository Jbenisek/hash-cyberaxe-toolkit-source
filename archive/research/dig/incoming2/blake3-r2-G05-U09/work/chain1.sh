
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/dig/incoming2/blake3-r2-G05-U09/work
date > chain1.log
echo "== cmin s0=0 cap8 relax0" >> chain1.log; ./actmodel cmin 0 8 0 1 65536 >> chain1.log
date >> chain1.log
for s in 1000 2000 3000 5000; do echo "== x0 s0=$s" >> chain1.log; ./actmodel x0 $s 0 65536 >> chain1.log; date >> chain1.log; done
for r in 2 4; do echo "== cmin s0=0 cap7 relax=$r" >> chain1.log; ./actmodel cmin 0 7 $r 1 65536 >> chain1.log; date >> chain1.log; done
echo DONE >> chain1.log
