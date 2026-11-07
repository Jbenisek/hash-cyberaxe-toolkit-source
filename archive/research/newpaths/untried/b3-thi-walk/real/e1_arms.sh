#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# e1_arms.sh: E1 outcome rate (seven outcomes, Lemma N's eps) on real 32-bit trials, 2^45 trials per arm (research only)
#   walk       2^16 groups (context, member) x 2^8 random steps of their full blocks x all of Q*
#   ctl        2^24 fresh (context, member) outer steps at t_hi = 0 (the front line) x all of Q*
#   walkdense  2^8 groups x 2^16 steps: per-group dispersion with everything but t_hi fixed (Y12, w12, w5 fixed)
#   ctxdense   2^8 contexts x 2^16 members at t_hi = 0: the front line's per-context dispersion (w12, w5 fixed)
D="${HASHCYBERAXE_WORKSPACE}"/research/newpaths/untried/b3-thi-walk/real
cd "$D" || exit 1
nvcc -O3 -arch=sm_86 -w -o bin/walk32 walk32.cu -lm 2>&1 | grep -v '^$' | head -30
sha256sum bin/walk32 > out/e1_bin.sha256
./bin/walk32 probe 2026101001 > out/probe2.txt
cmp out/probe.txt out/probe2.txt && echo "probe unchanged"
for A in "walk 65536 256 2026101011" "ctl 16777216 1 2026101012" "walk 256 65536 2026101013" "ctx 256 65536 2026101014"; do
  set -- $A
  ./bin/walk32 e1 $4 $2 $3 $1 > out/e1_${1}_G$2_S$3.txt
  echo "== $1 G $2 S $3 seed $4"; cat out/e1_${1}_G$2_S$3.txt
done
date
