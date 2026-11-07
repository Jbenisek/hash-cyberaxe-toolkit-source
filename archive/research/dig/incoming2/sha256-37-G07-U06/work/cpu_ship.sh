#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
S="${HASHCYBERAXE_WORKSPACE}"/research/tools/build_pkg/scratch
echo "load: $(cat /proc/loadavg)"
t(){ /usr/bin/time -f "$3 cpu_user=%U sys=%S wall=%e maxrss_KB=%M" python3 -B -s "$1" < "$2" 2>&1 >/tmp/u06_o | tail -1; sha256sum /tmp/u06_o | cut -c1-12; }
# control: fixed CPU-bound loop, run twice
for i in 1 2; do /usr/bin/time -f "control loop cpu_user=%U wall=%e" python3 -c "
x=0
for i in range(30000000): x+=i*i" 2>&1 | tail -1; done
for rep in 1 2; do for e in a0-sfs-r37 a0-online-r37; do t /tmp/u06_x.py $S/pkgR37X/work/req_$e.json "R37X $e rep$rep"; done; done
for e in a0-sfs-r37 a0-online-r37 a1-cv-r37 a3-ctl-r37 a3-dep-r37; do t /tmp/u06_x2.py $S/pkgR37X2/work/oreq_$e.json "R37X2 $e"; done
echo "load: $(cat /proc/loadavg)"
