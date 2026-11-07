
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
for R in 6 5; do
 cd "${HASHCYBERAXE_WORKSPACE}"/research/blake3_r$R/b8r$R && ( ulimit -v 2500000; nice -n 10 python3 -B appA.py > appA.out ) &
done
wait
