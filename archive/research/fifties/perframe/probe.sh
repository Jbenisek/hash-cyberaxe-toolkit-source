#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}/research/fifties/perframe"
nproc; free -g | head -2
python3 -B -c "
import sys; sys.path.insert(0,'../../pkg16/pkg/blake3-r2/experiments')
import halfsearch as H
fq, fe = H.ctr_tables()
print('fq', [len(t) for t in fq], 'fe', [len(t) for t in fe])
print('CLASS_SIZE', H.CLASS_SIZE, 'free', H.CLASS_FREE, hex(H.CLASS_MASK), hex(H.CLASS_VALUE))
print('Y3 %08x Y3B %08x Y11 %08x Y11B %08x DELTA5 %08x' % (H.Y3, H.Y3B, H.Y11, H.Y11B, H.DELTA5))
print('RULE_A', [(hex(m), v) for m, v in H.RULE_A])
print('maxval fq', max(max(t) for t in fq), 'fe', max(max(t) for t in fe))
"
