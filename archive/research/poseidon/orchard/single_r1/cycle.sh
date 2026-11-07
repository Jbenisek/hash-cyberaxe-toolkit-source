#!/bin/bash
# cycle.sh: one command from "code or claim changed" to "package staged and prefile-clean" for the single-centre Poseidon entry.
#   build -> evidence jobs (2 at a time, cached by source hash) -> collision certificates -> package -> prefile_check -> one-screen summary.
# usage:  bash cycle.sh [--fresh] [--stage]   (--fresh ignores the cache; every job runs; results are cached again;
#         --stage also runs stage_pkg.sh after the summary: copies the package into the pos_r1_single slot and runs the organizer's mechanical intake; never submits)
# env:    CAP=6 (DEG_CAP of the entry; 0 = the uncapped program)   SEEDS="110 103" (one attempt = one certificate; the first is the ledger run)
#         JOBS=2 (heavy processes at once)   NICE=10
# Caching: every job is keyed by sha256 over the local files that the job's C program includes (gcc -MM) + its arguments. Editing proof_template.md,
#   note_tail.py, build_package.py or the claim therefore re-runs only the package and prefile steps (seconds). Nothing here changes counted code:
#   the instrumented binary is built with the flags of build_cap.sh, the ledger run only adds the verbose flag (printing only) and ulimit -s 64.
# Files written: logs/cap<CAP>run_<seed>.txt, logs/calib_cap<CAP>.txt, logs/size_cap<CAP>.txt, pkg_stage_cap<CAP>/, submission-note_cap<CAP>.md, data/numbers_cap<CAP>.json,
#   pkg_check_cap<CAP>/ (what prefile_check reads), logs/cycle_last.txt (this summary), cache in data/cache/.
set -u
cd "$(dirname "$0")"
HERE=$PWD
CAP=${CAP:-6}; SEEDS=${SEEDS:-"110 103"}; JOBS=${JOBS:-2}; NICE=${NICE:-10}
FRESH=0; STAGE=0
for a_ in "$@"; do case $a_ in --fresh) FRESH=1;; --stage) STAGE=1;; *) echo "unknown option $a_"; exit 2;; esac; done
CACHE=$HERE/data/cache; T=$HERE/logs/cycle_times; PFX=cap${CAP}run_
mkdir -p "$CACHE" "$T" "$HERE/logs"; rm -f "$T"/*
LIBS="common.c ntt.c poly.c lean.c line.c split.c hgcd.c pallas.c"
CF="-O3 -march=native -Wall -Wextra -Wno-unused-function -Wno-unused-variable -Wno-unused-parameter"
GCCV=$(gcc --version | head -1)
now() { date +%s.%N; }
W0=$(now)
stamp() { # name t0 status
  printf '%s %s\n' "$(echo "$(now) - $2" | bc)" "$3" > "$T/$1"
}
dephash() { # extra-string, then gcc args (sources and -D flags): hash of all local files compiled/included + extra
  local extra="$1"; shift
  { echo "$extra"; gcc -MM "$@" 2>/dev/null | tr -d '\\' | tr -s ' \n' '\n\n' | grep -v ':$' | grep -v '^$' | sort -u | while read -r f; do sha256sum "$f"; done; } | sha256sum | cut -c1-16
}
DEFS=""; [ "$CAP" != 0 ] && DEFS="-DDEG_CAP=$CAP"
SRCS="single.c $LIBS"
CPU=$(grep -m1 'model name' /proc/cpuinfo | cut -d: -f2)
SKEY=$(dephash "$GCCV $CF $DEFS" $DEFS $SRCS)
echo "cycle: CAP=$CAP seeds=[$SEEDS] jobs=$JOBS fresh=$FRESH source-hash=$SKEY"

# ---- 1. build the instrumented program (cached binary per source hash)
t0=$(now); BIN=single_cap$CAP; [ "$CAP" = 0 ] && BIN=single
BD=$CACHE/bin/$SKEY-$(echo "$CPU" | sha256sum | cut -c1-6)
if [ $FRESH = 0 ] && [ -x "$BD/$BIN" ]; then st=cached; else
  mkdir -p "$BD"; gcc $CF $DEFS -o "$BD/$BIN.tmp" $SRCS -lm 2>"$BD/gcc.err" && mv "$BD/$BIN.tmp" "$BD/$BIN" || { echo "BUILD FAILED"; tail "$BD/gcc.err"; exit 2; }; st=built; fi
cmp -s "$BD/$BIN" "$BIN" || cp "$BD/$BIN" "$BIN"
size "$BIN" > logs/size_cap$CAP.txt
stamp 00_build $t0 $st

# ---- 2. evidence jobs
sig() { grep -E 'arith=|^SUMMARY|^TYPES|^gcd degree|^RESULT|^COLLISION|^SPLIT|^lean-pow|^r=' "$1" | sed -E 's/ +[0-9]+\.[0-9]s peak/ peak/; s/ secs=[0-9.]+//'; }
job_ledger() { # seed: the counted run (verbose = printing only; stack limit 64 KiB, the claim of the proof)
  local seed=$1 t0=$(now) key d out=logs/${PFX}$1.txt
  key=$(dephash "ledger cap=$CAP seed=$seed verbose=1 stack=64KiB $GCCV $CF" $DEFS $SRCS); d=$CACHE/ledger/$key
  if [ $FRESH = 0 ] && [ -s "$d/log.txt" ]; then cp "$d/log.txt" "$out"; stamp 10_ledger_$seed $t0 cached
  else
    ( ulimit -s 64; nice -n $NICE ./$BIN "$seed" 1 > "$out.tmp" 2>&1; echo "EXIT $?" >> "$out.tmp" )
    mv "$out.tmp" "$out"
    if grep -q '^SUMMARY' "$out"; then mkdir -p "$d"; cp "$out" "$d/log.txt"; stamp 10_ledger_$seed $t0 ran; else stamp 10_ledger_$seed $t0 FAILED; fi
  fi
  sig "$out" > "data/cycle_sig_${CAP}_$seed.new"
}
job_calib() { # calibration of the root isolation at the levels of the schedule (cap: only the levels 4 and 9)
  local t0=$(now) args="4 9 19 38 76 152 305 610 1220 2441 4882 9765 19531 39062"; [ "$CAP" != 0 ] && args="4 9"
  local key d; key=$(dephash "calib args=$args $GCCV $CF" calib.c $LIBS); d=$CACHE/calib/$key
  if [ $FRESH = 0 ] && [ -s "$d/calib.txt" ]; then cp "$d/calib.txt" logs/calib_cap$CAP.txt; stamp 20_calib $t0 cached; return; fi
  mkdir -p "$d"; gcc $CF -o "$d/calib" calib.c $LIBS -lm 2>"$d/gcc.err" || { stamp 20_calib $t0 FAILED; return; }
  ( nice -n $NICE "$d/calib" $args > "$d/calib.tmp" 2>&1; echo "EXIT $?" >> "$d/calib.tmp" ); mv "$d/calib.tmp" "$d/calib.txt"; rm -f "$d/calib"
  cp "$d/calib.txt" logs/calib_cap$CAP.txt; grep -q '^EXIT 0' "$d/calib.txt" && stamp 20_calib $t0 ran || stamp 20_calib $t0 FAILED
}
job_gcdb() { # worst-case gcd/division bounds header: regenerated and compared with gcd_bounds.h (never overwritten here)
  # the MONO ratio checks (stderr only, they test the 1.02 monotonicity heuristic of levels > 152) are skipped under the cap: those levels never run. The header is unchanged by them.
  local nm=${GCDB_NOMONO-}; [ -z "$nm" ] && [ "$CAP" != 0 ] && nm=1
  local t0=$(now) key d; key=$(dephash "gcdbound H nomono=$nm $GCCV" gcdbound.c common.c ntt.c poly.c lean.c line.c split.c pallas.c); d=$CACHE/gcdb/$key
  if [ $FRESH = 1 ] || [ ! -s "$d/gcd_bounds.h" ]; then
    mkdir -p "$d"; gcc -O3 -march=native -Wno-unused-function -Wno-unused-variable -Wno-unused-parameter -Wno-unused-but-set-variable -o "$d/gcdbound" gcdbound.c common.c ntt.c poly.c lean.c line.c split.c pallas.c -lm 2>"$d/gcc.err" || { stamp 30_gcdbound $t0 FAILED; return; }
    ( if [ -n "$nm" ]; then export NOMONO=1; else unset NOMONO; fi; nice -n $NICE "$d/gcdbound" H > "$d/h.tmp" 2> "$d/gcdbound.err"; echo "EXIT $?" >> "$d/gcdbound.err" ); rm -f "$d/gcdbound"
    grep -q '^EXIT 0' "$d/gcdbound.err" && mv "$d/h.tmp" "$d/gcd_bounds.h" || { stamp 30_gcdbound $t0 FAILED; return; }; st=ran
  else st=cached; fi
  if cmp -s "$d/gcd_bounds.h" gcd_bounds.h; then stamp 30_gcdbound $t0 "$st identical-to-gcd_bounds.h"; else stamp 30_gcdbound $t0 "$st DIFFERS-from-gcd_bounds.h(see $d)"; fi
}
job_keep() { # memory of the gcd stage of the root isolation at degree 39062 (uncapped program only)
  local t0=$(now) key d; key=$(dephash "test_keep $GCCV" test_keep.c $LIBS); d=$CACHE/keep/$key
  if [ $FRESH = 0 ] && [ -s "$d/test_keep.txt" ]; then cp "$d/test_keep.txt" logs/test_keep.txt; stamp 40_test_keep $t0 cached; return; fi
  mkdir -p "$d"; gcc -O3 -march=native -Wno-unused-function -Wno-unused-variable -Wno-unused-parameter -o "$d/tk" test_keep.c $LIBS -lm 2>/dev/null || { stamp 40_test_keep $t0 FAILED; return; }
  nice -n $NICE "$d/tk" 39062 > "$d/test_keep.txt" 2>&1; rm -f "$d/tk"; cp "$d/test_keep.txt" logs/test_keep.txt; stamp 40_test_keep $t0 ran
}
job_hgcd() { # half-gcd against classical Euclid on planted gcds (the "synthetic inputs" claim of the note)
  local t0=$(now) key d; key=$(dephash "test_hgcd v1 $GCCV" test_hgcd.c $LIBS); d=$CACHE/hgcd/$key
  if [ $FRESH = 0 ] && [ -s "$d/test_hgcd.txt" ]; then cp "$d/test_hgcd.txt" logs/test_hgcd_cap$CAP.txt; stamp 50_test_hgcd $t0 cached; return; fi
  mkdir -p "$d"; gcc -O3 -march=native -Wno-unused-function -Wno-unused-variable -Wno-unused-parameter -o "$d/th" test_hgcd.c $LIBS -lm 2>/dev/null || { stamp 50_test_hgcd $t0 FAILED; return; }
  { for a in "300 3 299" "1000 5 999" "1000 5 10" "1000 5 500" "1000 5 6" "3000 7 2999" "3000 0 100" "3000 10 600" "3000 0 2999" "5000 20 4999" "5000 20 3000" "20000 9 19999 0"; do nice -n $NICE "$d/th" $a; done; } > "$d/test_hgcd.txt" 2>&1; rm -f "$d/th"
  cp "$d/test_hgcd.txt" logs/test_hgcd_cap$CAP.txt
  [ "$(grep -c '^HGCD OK' "$d/test_hgcd.txt")" = 12 ] && stamp 50_test_hgcd $t0 ran || stamp 50_test_hgcd $t0 "ran-NOT-ALL-OK"
}
JL=""
# heaviest first; with the cap the ledger runs (about 90 s each) dominate, without it the calibration and test_split would too
for s in $SEEDS; do JL="$JL job_ledger:$s"; done
JL="$JL job_gcdb job_calib job_hgcd"; [ "$CAP" = 0 ] && JL="$JL job_keep"
t0=$(now)
for j in $JL; do
  while [ "$(jobs -rp | wc -l)" -ge "$JOBS" ]; do wait -n; done
  case $j in job_ledger:*) job_ledger "${j#*:}" & ;; *) $j & ;; esac
done
wait
JOBS_WALL=$(echo "$(now) - $t0" | bc)

# ledger signature check against the previous run (counts must not move when nothing counted changed)
SIGMSG=""
for s in $SEEDS; do
  n=data/cycle_sig_${CAP}_$s
  if [ -s $n.txt ]; then if cmp -s $n.txt $n.new; then SIGMSG="$SIGMSG seed$s:identical"; else SIGMSG="$SIGMSG seed$s:CHANGED"; fi; else SIGMSG="$SIGMSG seed$s:first"; fi
  mv -f $n.new $n.txt
done

# ---- 3. certificates, package, prefile
PY=python3
FIRST=${SEEDS%% *}
export CAP LOGPREFIX=$PFX LEDGER=${PFX}$FIRST.txt PKG_OUT=pkg_stage_cap$CAP SIZE_FILE=logs/size_cap$CAP.txt NOTE_OUT=submission-note_cap$CAP.md NUMBERS=numbers_cap$CAP.json CALIB=logs/calib_cap$CAP.txt COLLS=collisions_cap$CAP.json
t0=$(now); $PY collect.py $PFX $COLLS > logs/collect_cap$CAP.txt 2>&1; $PY verify_collision.py logs/${PFX}*.txt > logs/verify_cap$CAP.txt 2>&1; VER=$?
stamp 60_certificates $t0 $([ $VER = 0 ] && echo verified || echo VERIFY-FAILED)
t0=$(now); $PY build_package.py > logs/build_package_cap$CAP.txt 2>&1; BP=$?
stamp 70_package $t0 $([ $BP = 0 ] && echo ok || echo FAILED)
if [ $BP != 0 ]; then tail -5 logs/build_package_cap$CAP.txt; fi
CHK=$HERE/pkg_check_cap$CAP; rm -rf "$CHK"; mkdir -p "$CHK/poseidon-orchard-r1"; cp -r "$HERE/pkg_stage_cap$CAP/." "$CHK/poseidon-orchard-r1/"; cp "$HERE/submission-note_cap$CAP.md" "$CHK/submission-note.md"
t0=$(now); $PY ../../../launch/prefile_check.py "$CHK" > logs/prefile_cap$CAP.txt 2>&1; stamp 80_prefile $t0 done

# ---- 4. summary
{
echo "=== cycle summary  CAP=$CAP seeds=[$SEEDS]  source-hash $SKEY"
for f in "$T"/*; do printf '  %-18s %8.1f s  %s\n' "$(basename "$f" | cut -c4-)" $(cut -d' ' -f1 "$f") "$(cut -d' ' -f2- "$f")"; done
SERIAL=$(cat "$T"/* | awk '{s+=$1} END {printf "%.1f", s}')
printf '  %-18s %8.1f s  (sum of steps %s s; evidence jobs ran %s at a time: %.1f s wall)\n' "TOTAL WALL" "$(echo "$(now) - $W0" | bc)" "$SERIAL" "$JOBS" "$JOBS_WALL"
echo "  ledger counts vs previous run:$SIGMSG"
if [ -s data/numbers_cap$CAP.json ]; then
$PY - <<EOF
import json
n = json.load(open('data/numbers_cap$CAP.json'))
print('  time_log2 %.5f (exact %.5f)   memory %d bytes (log2 %.3f)   score %.5f   certificates %d   worst-case ops %s' % (n['time'], n['time_exact'], n['mem_bytes'], n['mem_log2'], n['score'], n['n_cert'], format(n['worst'], ',')))
EOF
fi
grep -h 'evidence estimate' logs/prefile_cap$CAP.txt | sed 's/(ROUGH.*//; s/^/  /'
echo "  prefile: $(tail -1 logs/prefile_cap$CAP.txt)"; grep '^FAIL' logs/prefile_cap$CAP.txt | cut -c1-150 | sed 's/^/    /'
} | tee logs/cycle_last.txt

if [ $STAGE = 1 ]; then echo "--- staging (stage_pkg.sh)"; bash ./stage_pkg.sh 2>&1 | tail -25; fi
