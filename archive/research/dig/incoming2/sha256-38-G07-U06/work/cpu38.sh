#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# RULE (written before the run): pass iff max CPU user seconds < 20.0 per experiment run (organizer timeout_seconds 20.0, one CPU).
W="${HASHCYBERAXE_WORKSPACE}"/research/dig/incoming2/sha256-38-G07-U06/work
S="${HASHCYBERAXE_WORKSPACE}"/research/tools/build_pkg/scratch
cp $S/pkgR38L/pkg/sha256-r38/experiments/vt38.py /tmp/u06b_L.py
cp $S/pkgR38N/pkg/sha256-r38/experiments/vt38.py /tmp/u06b_N.py
cp $S/pkgR38M3/pkg/sha256-r38/experiments/a0lean38.py /tmp/u06b_M3.py
echo "load: $(cat /proc/loadavg)"
t(){ /usr/bin/time -f "$3 cpu_user=%U sys=%S wall=%e maxrss_KB=%M" python3 -B -s "$1" < "$2" 2>&1 >/tmp/u06b_o | tail -1; echo "   out_sha=$(sha256sum /tmp/u06b_o | cut -c1-12) bytes=$(wc -c </tmp/u06b_o)"; }
for i in 1 2; do /usr/bin/time -f "control loop cpu_user=%U wall=%e" python3 -c "
x=0
for i in range(30000000): x+=i*i" 2>&1 | tail -1; done
for rep in 1 2; do for e in vt-q3-smc-r38 vt-ram-r38; do t /tmp/u06b_L.py $W/req_L_${e}_pub.json "L(shipped fdef4bab) $e pub rep$rep"; done; done
for e in vt-q3-smc-r38 vt-ram-r38; do t /tmp/u06b_L.py $W/req_L_${e}_fresh.json "L $e fresh"; done
for e in vt-q3-smc-r38 vt-ram-r38; do t /tmp/u06b_N.py $W/req_N_${e}_pub.json "N(cfeb996a) $e pub"; done
for e in a0-online-r38 a0-q3-r38; do t /tmp/u06b_M3.py $W/req_M3_${e}_pub.json "M3(staged) $e pub"; done
echo "load: $(cat /proc/loadavg)"
