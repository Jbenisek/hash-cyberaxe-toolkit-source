
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/dig/incoming2/blake3-r2-G05-U12/work
gcc -O3 -march=native -std=gnu11 -o trunc_relax trunc_relax.c || exit 1
for R in 0 2 4; do s=$(date +%s); RELAX=$R ./trunc_relax -1 0 256 res_relax$R.bin Tdump.bin > relax$R.log 2>&1; echo "RELAX=$R rc=$? wall=$(( $(date +%s)-s ))s" >> c.log; cmp -s res_relax$R.bin ref/res_relax$R.bin && echo same >> c.log || echo differs >> c.log; done
