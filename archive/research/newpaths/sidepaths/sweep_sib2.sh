#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# random same-parity triples of lengths 1..64 (base length = smallest): any pin with equal C3 (b,d) for all three?
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/sidepaths
mkdir -p sib2
out=sweep_sib2.txt
: > $out
python3 - <<'EOF' > sib2/list.txt
import random
r = random.Random(5)
seen = set()
while len(seen) < 40:
    p = r.randrange(2)
    t = tuple(sorted(r.sample([L for L in range(1, 65) if L % 2 == p], 3)))
    seen.add(t)
for t in sorted(seen):
    print(*t)
EOF
while read a b c; do
  f=sib2/t_${a}_${b}_${c}.smt2
  # triple_smt.py writes a1_L = T + (Q ^ 55 ^ L); Q is free, so this covers any set of lengths
  python3 triple_smt.py $a,$b,$c $f
  r=$(timeout 60 z3 -T:55 $f 2>&1 | head -1)
  echo "triple $a $b $c $r" >> $out
done < sib2/list.txt
echo done > sweep_sib2.done
