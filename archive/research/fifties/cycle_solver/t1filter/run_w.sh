
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}/research/fifties/cycle_solver/t1filter"
/usr/bin/time -f "%e s ref" ../../split_e3/solve inst_w.txt ref_w.txt > ref_w.log 2>&1 &
./bsolve batch_w.txt 19 table 0 8 out_w19_a.txt 2> log_w19_a.txt &
./bsolve batch_w.txt 19 table 8 16 out_w19_b.txt 2> log_w19_b.txt &
./bsolve batch_w.txt 19 table 16 24 out_w19_c.txt 2> log_w19_c.txt &
wait
echo w19 > done_w19.txt
./bsolve batch_w.txt 24 table 0 8 out_w24_a.txt 2> log_w24_a.txt &
./bsolve batch_w.txt 24 table 8 16 out_w24_b.txt 2> log_w24_b.txt &
./bsolve batch_w.txt 24 table 16 24 out_w24_c.txt 2> log_w24_c.txt &
wait
echo w24 > done_w24.txt
./bsolve batch_w.txt 28 stream 0 8 out_w28_a.txt 2> log_w28_a.txt &
./bsolve batch_w.txt 28 stream 8 16 out_w28_b.txt 2> log_w28_b.txt &
./bsolve batch_w.txt 28 stream 16 24 out_w28_c.txt 2> log_w28_c.txt &
wait
echo w28 > done_w28.txt