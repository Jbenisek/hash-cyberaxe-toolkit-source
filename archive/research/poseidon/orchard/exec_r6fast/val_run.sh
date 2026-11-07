#!/bin/bash
# Validation run (local WSL, nice 10): bash val_run.sh RR T TAG [gcc flags]
#   builds /tmp/r6fast_val/<TAG>/single from the exec_r6fast sources (flags as exec_r6mt/cycle.sh, arena per RR), runs `single 1 T` under ulimit -s 64,
#   copies the ledger to exec_r6fast/val_out/<TAG>.txt and prints the trial lines, SUMMARY, THREADS and the md5 of the COLLISION lines.
#   A run whose first success is not centre 1 (RR=3) / centre 2 (RR=4) is repeated once (the local machine has shown non-reproducible failed trials under load).
set -u
RR=$1; T=$2; TAG=$3; shift 3; EXTRA="$*"
SRC=$(cd "$(dirname "$0")" && pwd)
case $RR in 3) AR=290000000ULL; WANT=1;; 4) AR=1227182400ULL; WANT=2;; *) AR=6400000000ULL; WANT=1;; esac
D=/tmp/r6fast_val/$TAG; rm -rf $D; mkdir -p $D; cp $SRC/*.c $SRC/*.h $D/; cd $D
CF="-O3 -march=native -mcmodel=medium -static -nostdlib -fno-stack-protector -U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=0 -fno-pie -no-pie -ffunction-sections -fdata-sections -Wl,--gc-sections -Wall -Wextra -Wno-unused-function -Wno-unused-variable -Wno-unused-parameter"
gcc $CF -DRR=$RR -DARENA=$AR $EXTRA -o single single.c common.c ntt.c poly.c lean.c line.c split.c hgcd.c pallas.c par.c nolibc.c 2> build.err; echo "[$TAG] build rc=$? warnings=$(grep -c warning build.err) flags: $EXTRA"
mkdir -p $SRC/val_out
for attempt in $(seq 1 ${ATT:-2}); do
  s0=$(date +%s)
  ( ulimit -s 64; nice -n 10 ./single 1 $T 1 $WANT > run.txt 2>&1; echo "EXIT $?" >> run.txt )   # trial cap = the known first success (speculative-run arguments); a faulty run stops early
  s1=$(date +%s)
  cp run.txt $SRC/val_out/${TAG}_a$attempt.txt
  C=$(grep -a -o 'COLLISION centre 0x[0-9a-f]*' run.txt | sed 's/.*0x0*//')
  echo "[$TAG] attempt $attempt: wall $((s1 - s0)) s; first success centre ${C:-none}"
  grep -a -E '^trial|^TRIALS|SUMMARY|^THREADS|^EXIT|  [BCD]:' run.txt | cut -c1-200
  echo "[$TAG] COLLISION md5 $(grep -a '^COLLISION' run.txt | md5sum | cut -c1-32)"
  [ "${C:-0}" = "$WANT" ] && break
done
