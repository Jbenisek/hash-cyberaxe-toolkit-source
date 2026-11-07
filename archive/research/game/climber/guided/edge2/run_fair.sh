#!/usr/bin/env bash
# run_fair.sh : fair speed test - the NORMAL setup (released hyb38 A10 xml, nothing pinned, cv free, no cap) on 2 seeds, vs the tunnel method (542 s).
D="$(cd "$(dirname "$0")" && pwd)"; G=$D/..; OUT=$D/RESULTS_fair.tsv; ENC=$G/relscan/sha_cnf.py
lane() { name=$1; xml=$2; s=$3; b=/dev/shm/edge2_${name}; o=$D/${name}_s$s
  [ -f $b.cnf ] || SIGNED=1 python3 $ENC $xml $b.cnf $b.map sfs > /dev/null || { echo -e "$name\ts$s\tBUILDFAIL" >> $OUT; return; }
  t0=$(date +%s); echo -e "$name\ts$s\tSTART\t$(date '+%H:%M')" >> $OUT
  nice -n 10 kissat --seed=$s $b.cnf > $o.out 2>&1 & k=$!
  while kill -0 $k 2>/dev/null; do sleep 60; [ $(( ($(date +%s)-t0) % 1800 )) -lt 60 ] && kill -0 $k 2>/dev/null && echo -e "$name\ts$s\tRUNNING\t$(( ($(date +%s)-t0)/60 )) min" >> $OUT; done
  wait $k; rc=$?; case $rc in 10) v=SAT;; 20) v=UNSAT;; *) v=ERR$rc;; esac
  if [ $v = SAT ]; then grep '^v' $o.out | sed 's/^v //' > $o.model; python3 $ENC --decode $b.map $o.model > $D/FOUND_${name}_s$s.txt 2>&1
    grep -q "outputs equal: True" $D/FOUND_${name}_s$s.txt || v=SAT_CHECKFAIL; fi
  echo -e "$name\ts$s\t$v\t$(( $(date +%s)-t0 ))s" >> $OUT; }
X=$G/relscan/cells/hyb38_pin38_to_pin38b_s17g5/rel_hyb38_pin38_to_pin38b_s17g5_A10.xml
lane fair_hyb38_A10 $X 1 & sleep 20; lane fair_hyb38_A10 $X 2 & wait; echo FAIR DONE; cat $OUT
