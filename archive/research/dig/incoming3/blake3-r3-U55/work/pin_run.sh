#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}/research/dig/incoming3/blake3-r3-U55/work"
gcc -O3 -march=native -o pintest pintest.c -lm || exit 1
rm -f pin_all.txt
nice -n 10 ./pintest 0 1000 3 4 0 >> pin_all.txt
nice -n 10 ./pintest 0 1000 3 4 1 >> pin_all.txt
for p in 4 5 6 7; do
  nice -n 10 ./pintest 4 100 3 $p 0 >> pin_all.txt
done
nice -n 10 ./pintest 4 100 3 4 1 >> pin_all.txt
nice -n 10 ./pintest 8 12 3 4 0 >> pin_all.txt
nice -n 10 ./pintest 8 12 3 4 1 >> pin_all.txt
echo finished >> pin_all.txt
