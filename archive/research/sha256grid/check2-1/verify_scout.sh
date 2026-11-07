#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}/research/sha256grid/check2-1" || exit 1
S="${HASHCYBERAXE_WORKSPACE}/research/sha256grid/scout2-1"
python3 indep_verify.py $S/step1_base.sols.json $S/step1_k1r16.sols.json $S/step1_g32.sols.json $S/step1_g8.sols.json 2>&1 | tee verify_scout.txt
echo "--- negative controls (one bit of A13 / A2 / A0 flipped in S*):"
python3 - <<'EOF'
import sys; sys.argv = ['x']
exec(open('indep_verify.py').read().split("if __name__ == '__main__':")[0])
PAx, _, _ = forward(PCV, PMX); S = PAx[:16]
for i, b in ((13, 5), (2, 7), (0, 3), (15, 0)):
    T = list(S); T[i] ^= 1 << b
    bad, info = check(T)
    print('flip A%d bit %d: failures %s' % (i, b, bad[:6]))
EOF
