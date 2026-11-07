#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
W="${HASHCYBERAXE_WORKSPACE}"/research/dig/incoming2/sha256-38-G07-U06/work
IMG='python:3.12.12-slim-bookworm@sha256:2986c55feb36e6cae00fa1fefb454283e4b33f35e75ff8bdd123b134130be301'
echo "load: $(cat /proc/loadavg)"
for e in vt-q3-smc-r38 vt-ram-r38; do
 s=$(date +%s.%N)
 docker run --rm -i --pull=never --network none --cpus 1 --memory 128m -v /tmp/u06b_L.py:/input/program.py:ro "$IMG" python -B -s -P /input/program.py < $W/req_L_${e}_pub.json | sha256sum | cut -c1-12 > /tmp/u06b_h
 echo "docker L $e wall $(echo "$(date +%s.%N) - $s" | bc) s out=$(cat /tmp/u06b_h)"
done
echo "load: $(cat /proc/loadavg)"
