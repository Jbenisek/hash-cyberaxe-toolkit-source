#!/bin/bash
# remaining 9/10-word shapes for the Y13 release that could split below 2^92 (see RESULTS): 6 processes
cd "$(dirname "$0")"
gcc -O3 -march=native -o corexp corexp.c 2>&1 | grep -i error; gcc -O3 -march=native -o splitz splitz.c 2>&1 | grep -i error
m=part_02_t0_Y13
run() { r=$1; e=$2; d=$3; tag=r${r}e${e}d${d}
  for p in 0 1 2 3 4 5; do ( timeout 3000 ./corexp models/$m.mdl $r $e $d $p 6 > res/cx_${m}_${tag}_p$p.sol 2> res/cx_${m}_${tag}_p$p.log ) & done; wait
  cat res/cx_${m}_${tag}_p*.sol > res/cx_${m}_${tag}.sol; cat res/cx_${m}_${tag}_p*.log > res/cx_${m}_${tag}.log; rm -f res/cx_${m}_${tag}_p*
  n=$(grep -c '^SOL' res/cx_${m}_${tag}.sol); echo "$tag cores $(grep -c "^core " res/cx_${m}_${tag}.log) finished-procs $(grep -c "^cores" res/cx_${m}_${tag}.log)/6 sets $n" >> res/corex4.log
  if [ "$n" != "0" ]; then timeout 3000 ./splitz models/$m.mdl res/cx_${m}_${tag}.sol 5 80 1000000000 $r > res/split_cx_${m}_${tag}.txt 2>/dev/null; echo "$tag $(grep '^solutions' res/split_cx_${m}_${tag}.txt) $(grep '^histogram' res/split_cx_${m}_${tag}.txt)" >> res/corex4.log; fi
}
run 3 7 1
run 5 4 3
run 3 6 2
run 4 5 2
run 4 6 2
echo COREX4DONE >> res/corex4.log
