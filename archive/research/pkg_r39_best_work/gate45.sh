#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# gate45.sh : Failure stop 4 (STALE scan against the template = dkuthoore's 0b2616e3 package) and stop 5 (the package's own experiments on the staged files).
W="${HASHCYBERAXE_WORKSPACE}"/research
echo "=== STOP 4: prefile_scan vs dk template ==="
python3 $W/launch/prefile_scan.py $W/pkg_r39_best $W/pkg_r39_best_work/dkbase 2>&1 | grep -vE "^NEW FILE|^changed lines" | head -60
echo "=== STOP 5: experiments on the staged slot ==="
S=/root/hashsmash/yukon/pos_f1027004211/pareto/candidates/sha256/experiments
cd $S || exit 1
for e in r39-transplant-claw r39-window-small; do t0=$(date +%s.%N); python3 -B r39joint.py < $W/pkg_r39_best_work/exp/$e.json > /tmp/g5_$e.json 2>/tmp/g5_$e.err; echo "$e rc=$? $(echo "$(date +%s.%N)-$t0"|bc) s $(tail -c 200 /tmp/g5_$e.err)"; done
for i in 01 07 14; do t0=$(date +%s.%N); python3 -B r39tail.py < $W/pkg_r39_best_work/tail/r39-tail-$i.json > /tmp/g5_t$i.json 2>/tmp/g5_t$i.err; echo "r39-tail-$i rc=$? $(echo "$(date +%s.%N)-$t0"|bc) s $(tail -c 200 /tmp/g5_t$i.err)"; done
