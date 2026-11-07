#!/bin/bash
# usage: cv_run.sh <timeout> <nprocs> <k> <Ffixed> <model>
cd "$(dirname "$0")"
gcc -O3 -march=native -o gdcv gdcv.c 2>/dev/null
to=$1; np=$2; k=$3; F=$4; m=$5
for ((p=0; p<np; p++)); do
  ( timeout $to ./gdcv models/$m.mdl $k $F $p $np 100 1 > res/cv_${m}_k$k.p$p; echo "exit=$?" >> res/cv_${m}_k$k.p$p ) &
done
wait
cat res/cv_${m}_k$k.p* > res/cv_${m}_k$k.out; rm -f res/cv_${m}_k$k.p*
echo "$m k=$k: $(grep -c '^SOL' res/cv_${m}_k$k.out) staged solutions with J>=c; exits: $(grep exit res/cv_${m}_k$k.out | sort | uniq -c | tr '\n' ' ')" >> res/cv.log
grep HIST res/cv_${m}_k$k.out >> res/cv.log
