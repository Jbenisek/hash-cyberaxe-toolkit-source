
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}/research/fifties/cycle_solver/t1filter"
/usr/bin/time -f "%e s ref" ../../split_e3/solve inst_v.txt ref_v.txt > ref_v.log 2>&1
./bsolve batch_v.txt 19 table 0 8 out_v19_a.txt 2> log_v19_a.txt &
./bsolve batch_v.txt 19 table 8 16 out_v19_b.txt 2> log_v19_b.txt &
./bsolve batch_v.txt 19 table 16 24 out_v19_c.txt 2> log_v19_c.txt &
wait
echo done > done_v19.txt
