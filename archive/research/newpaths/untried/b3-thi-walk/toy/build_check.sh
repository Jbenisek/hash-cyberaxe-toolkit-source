#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# build_check.sh: build ctr_walk (W = 8) and reproduce the rig's quick validation at the old base (control arm,
# thi = 0, NT = 1: must equal the rig's GPU port line for line on trials, t = 0 and hits), then a smoke walk.
D="${HASHCYBERAXE_WORKSPACE}"/research/newpaths/untried/b3-thi-walk/toy
Q="${HASHCYBERAXE_WORKSPACE}"/research/impl/toy8_prereg/val/quick_gpu_set0.txt
cd "$D" || exit 1
mkdir -p bin out
nvcc -O3 -arch=sm_86 -DWBITS=8 -w -o bin/ctr_walk8 ctr_walk.cu -lm 2>&1 | grep -v '^$' | head -30
sha256sum bin/ctr_walk8
./bin/ctr_walk8 run 820261008 sets_w8.txt 0 bf 0 4 2048 0 1 1000 > out/check_old_base_set0.txt
grep -E '^(PART)' out/check_old_base_set0.txt
grep -E '^HIT' "$Q" | awk '{for(i=1;i<=NF;i++){if($i=="outer")o=$(i+1);if($i=="x2")x=$(i+1);if($i=="member")m=$(i+1);if($i=="d1")d=$(i+1);if($i=="t")t=$(i+1);if($i=="run")r=$(i+1)}; print "rig run",r,"outer",o,"x2",x,"member",m,"d1",d,"t",t}'
grep -E '^HIT' out/check_old_base_set0.txt | awk '{printf "walk run %s g %s (outer %d x2 %x) k %s d1 %s t %s fwd %s cv %s tree %s\n",$5,$7,int($7/256),$7%256,$9,$15,$19,$21,$23,$25}'
grep -E '^RUN' "$Q" | awk '{print "rig", $6, $16, $18, $22}'
grep -E '^RUN' out/check_old_base_set0.txt | awk '{print "walk", $5, $12, $14, $18}'
# smoke: the walk arm on set 0, 8 runs, NT = 32
./bin/ctr_walk8 run 12345 sets_w8.txt 0 bf 0 8 64 0 32 50 > out/smoke_walk_set0.txt
grep -E '^(HEAD|PART)' out/smoke_walk_set0.txt
grep -c '^HIT' out/smoke_walk_set0.txt
date
