#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# run_arms.sh: the three arms of PLAN.txt, one GPU process at a time (research only)
D="${HASHCYBERAXE_WORKSPACE}"/research/newpaths/untried/b3-thi-walk/toy
cd "$D" || exit 1
sha256sum PLAN.txt > PLAN.sha256
BETA=(bf b3 b3 b3 33 b3 bf bf)
NC=(2048 1170 1170 964 4096 745 2048 2048)
N32=(64 37 37 30 128 23 64 64)
N256=(8 5 5 4 16 3 8 8)
base() { python3 -c "import hashlib,sys; print(int.from_bytes(hashlib.sha256(('b3-thi-walk toy 2026-10-10 arm '+sys.argv[1]).encode()).digest()[:8],'little'))" "$1"; }
echo "$(date '+%F %T') start plan $(cut -c1-16 PLAN.sha256)" >> out/arms.log
for ARM in C W32 W256; do
  B=$(base $ARM)
  echo "$(date '+%F %T') arm $ARM base $B" >> out/arms.log
  for i in 0 1 2 3 4 5 6 7; do
    case $ARM in
      C) N=${NC[$i]}; NT=1; CAP=2000;;
      W32) N=${N32[$i]}; NT=32; CAP=100;;
      W256) N=${N256[$i]}; NT=256; CAP=20;;
    esac
    f=out/${ARM}_set$i.txt
    ./bin/ctr_walk8 run "$B" sets_w8.txt $i ${BETA[$i]} 0 1280 $N 0 $NT $CAP > "$f.part" 2> "$f.err"
    if tail -1 "$f.part" | grep -q '^END$'; then mv "$f.part" "$f"; rm -f "$f.err"; st=done; else st=FAILED; fi
    echo "$(date '+%F %T') $ARM set $i $st $(grep '^PART' $f 2>/dev/null)" >> out/arms.log
  done
done
echo "$(date '+%F %T') end" >> out/arms.log
