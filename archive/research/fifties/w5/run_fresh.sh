#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# w5 (lever 14) fresh confirmation run: prereg8 binary unchanged, ctx arm only, new label keys,
# 2^17 contexts per generator x 2^19 members x k = 512 c1 = 2^45 trials per generator (2^46 total).
# Hit mask 2 = E1L hits dumped. Writes only under research/fifties/w5/fresh.
D="${HASHCYBERAXE_WORKSPACE}"/research/fifties/w5
B="${HASHCYBERAXE_WORKSPACE}"/research/impl/memberloop/prereg8/prereg8
K1=$(python3 -c "import hashlib;print(hashlib.sha256(b'HashSmash fifties w5 lever14 fresh ctx run 2026-10-09 | G1').hexdigest())")
K2=$(python3 -c "import hashlib;print(hashlib.sha256(b'HashSmash fifties w5 lever14 fresh ctx run 2026-10-09 | G2').hexdigest())")
mkdir -p $D/fresh
echo "{\"key_g1\":\"$K1\",\"key_g2\":\"$K2\"}" > $D/fresh/keys.json
echo $$ > $D/fresh/pid
for s in $(seq 0 31); do
  t=$(printf %02d $s)
  for g in 1 2; do
    if [ $g = 1 ]; then K=$K1; else K=$K2; fi
    $B run 0 $g $K $((s*4096)) 4096 512 $D/fresh/s${t}_g$g.bin $D/fresh/s${t}_g$g.hits 2 64 >> $D/fresh/run.log 2>> $D/fresh/run.err || echo "FAIL s$t g$g" >> $D/fresh/run.log
  done
done
echo DONE >> $D/fresh/run.log
