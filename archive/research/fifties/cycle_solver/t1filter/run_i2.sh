
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}/research/fifties/cycle_solver/t1filter"
./bsolve batch_i2.txt 19 stream 0 104 out_i2_a.txt 2> log_i2_a.txt &
./bsolve batch_i2.txt 19 stream 104 300 out_i2_b.txt 2> log_i2_b.txt &
wait
echo i2 > done_i2.txt