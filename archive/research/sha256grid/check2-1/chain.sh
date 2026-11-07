#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# check2-1 runner: one detached chain of kissat runs (sequential, so one solver process per chain).
# usage: chain.sh CHAINNAME "CNF TAG SEED TIME" ["CNF TAG SEED TIME" ...]
# Each run: kissat --time=TIME --seed=SEED CNF > TAG.out; TAG.pid holds the kissat PID; TAG.done has rc and wall.
# After a SAT run the model is decoded with the scout's decoder (copied here) into this folder only.
cd "${HASHCYBERAXE_WORKSPACE}/research/sha256grid/check2-1" || exit 1
NAME=$1; shift
printf '%s\n' "$@" > "$NAME.plan"
setsid nohup bash -c '
  cd "${HASHCYBERAXE_WORKSPACE}/research/sha256grid/check2-1"
  echo $$ > '"$NAME"'.chainpid
  while read -r CNF TAG SEED TIME; do
    [ -z "$CNF" ] && continue
    s=$(date +%s.%N)
    kissat --time=$TIME --seed=$SEED $CNF > $TAG.out 2>&1 &
    k=$!; echo $k > $TAG.pid
    wait $k; rc=$?
    e=$(date +%s.%N)
    echo "rc=$rc start=$s end=$e wall=$(echo "$e - $s" | bc)" > $TAG.done
    if [ $rc -eq 10 ]; then python3 gen_step1.py decode $CNF $TAG.out > $TAG.decode.txt 2>&1; fi
  done < '"$NAME"'.plan
  date > '"$NAME"'.chaindone
' > /dev/null 2>&1 < /dev/null &
sleep 1
echo "chain $NAME started, wrapper pid $(cat $NAME.chainpid 2>/dev/null)"; cat "$NAME.plan"; date
