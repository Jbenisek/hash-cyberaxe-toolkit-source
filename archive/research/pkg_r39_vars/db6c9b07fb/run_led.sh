#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# run_led.sh LO HI LANES : ledger windows LO..HI of this pair's program, LANES at a time, nice 10 (led_pair.sh pc, lane-capped).
P="${HASHCYBERAXE_WORKSPACE}"/research/pkg_r39_vars/db6c9b07fb
D=$HOME/r39vars/db6c9b07fb; mkdir -p $D $P/led; cp $P/r39joint.py $D/; cd $D
seq $1 $2 | xargs -P $3 -I{} sh -c "nice -n 10 python3 -B r39joint.py --windows 1 --seed {} --check --out $P/led/win_{}.json > $P/led/win_{}.txt 2>&1"
echo ALLDONE $(ls $P/led | grep -c json)
