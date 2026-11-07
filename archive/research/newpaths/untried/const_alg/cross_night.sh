#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# cross_night.sh: second calculator on the new pin's beta, as the night's cand_exact_lx.sh ran it
# (~/hashsmash/bin/night_pair_calc, executed only), but with ONE thread (OMP_NUM_THREADS=1) and a 900 s limit.
# Also the same binary on L4b 907df8c2 and L8b 82d58088 is not needed (the night already printed those parts).
D="${HASHCYBERAXE_WORKSPACE}/research/newpaths/untried/const_alg"
B="$HOME/hashsmash/bin/night_pair_calc"
echo "$(date +%H:%M:%S) cross_night pid $$ binary $(sha256sum "$B" | cut -c1-16)" | tee -a "$D/pids.txt" >> "$D/exact.log"
r=$(OMP_NUM_THREADS=1 nice -n 5 timeout 900 "$B" c972a031 bf0ab0ef 00000006 9b472fe7 a031fb8f 13140f5f 31 -y11 e035a78c 2>&1)
echo "night_pair_calc N6a 13140f5f exit $?: $(echo "$r" | grep -E 'positive|^EXACT' | tr '\n' ' ' | cut -c1-600)" >> "$D/exact.log"
echo "$(date +%H:%M:%S) cross_night done" >> "$D/exact.log"
