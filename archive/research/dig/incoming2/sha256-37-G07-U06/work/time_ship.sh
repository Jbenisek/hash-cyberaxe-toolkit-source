#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
S="${HASHCYBERAXE_WORKSPACE}"/research/tools/build_pkg/scratch
IMG='python:3.12.12-slim-bookworm@sha256:2986c55feb36e6cae00fa1fefb454283e4b33f35e75ff8bdd123b134130be301'
cp $S/pkgR37X/pkg/sha256-r37/experiments/xtab.py /tmp/u06_x.py
cp $S/pkgR37X2/pkg/sha256-r37/experiments/xtab.py /tmp/u06_x2.py
echo "load: $(cat /proc/loadavg)"
run(){ # prog req label
  s=$(date +%s.%N)
  docker run --rm -i --pull=never --network none --cpus 1 --memory 128m -v $1:/input/program.py:ro "$IMG" python -B -s -P /input/program.py < "$2" | sha256sum | cut -c1-12 > /tmp/u06_h
  echo "$3 $(echo "$(date +%s.%N) - $s" | bc) s out=$(cat /tmp/u06_h)"
}
for rep in 1 2 3; do for e in a0-sfs-r37 a0-online-r37; do
  run /tmp/u06_x.py $S/pkgR37X/work/req_$e.json "R37X $e rep$rep"; done; done
for e in a0-sfs-r37 a0-online-r37 a1-cv-r37 a3-ctl-r37 a3-dep-r37; do
  run /tmp/u06_x2.py $S/pkgR37X2/work/oreq_$e.json "R37X2 $e"; done
echo "load: $(cat /proc/loadavg)"
