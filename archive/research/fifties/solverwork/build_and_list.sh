#!/bin/bash
# build_and_list.sh (fifties/solverwork): build passgpu (prereg7 kernel, flags 3) and passgpu11 (root flags 11), list the
# T != 0 steps of both walks, static count check, false-negative check, small timing run.
# Usage: build_and_list.sh PER_STREAM_LOG2 FNCHECK_N
set -e
cd "$(dirname "$0")"
L=${1:-29}
FN=${2:-524288}
rm -f pass_list.txt measure_250.json
python3 -B gen_pass.py
/usr/bin/nvcc -O3 -arch=sm_86 -o passgpu passgpu.cu 2>/dev/null
/usr/bin/nvcc -O3 -arch=sm_86 -o passgpu11 passgpu11.cu 2>/dev/null
sha256sum passgpu.cu passgpu11.cu ../../pkg19/as_subset/prereg7/v7gpu.cu
diff <(grep -v pass_kernel passgpu.cu) ../../pkg19/as_subset/prereg7/v7gpu.cu | head -5 || true
SEEDS=$(python3 -B -c "import sys; sys.path.insert(0,'../../pkg19/as_subset/prereg7'); import run_prereg as R; print(' '.join(map(str,R.MAIN_SEEDS)))")
echo "seeds $SEEDS"
PER=$((1 << L))
CHUNK=$((1 << 26))
for W in P R; do
  B=passgpu; [ $W = R ] && B=passgpu11
  t0=$(date +%s.%N)
  ./$B p $PER $CHUNK $SEEDS pass_list_$W.txt 600000
  echo "walk $W gpu seconds $(echo "$(date +%s.%N) - $t0" | bc)"
  grep '^#' pass_list_$W.txt
done
python3 -B solver_measure.py static P > static_check.json
python3 -B solver_measure.py fncheck P $FN
python3 -B solver_measure.py fncheck R $FN
python3 -B solver_measure.py run P 250 8
python3 -B solver_measure.py run R 250 8
