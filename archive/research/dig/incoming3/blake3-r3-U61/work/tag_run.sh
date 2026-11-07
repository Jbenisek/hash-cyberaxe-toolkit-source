#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}/research/dig/incoming3/blake3-r3-U61/work"
gcc -O3 -march=native -o tagtest tagtest.c -lm || exit 1
rm -f tag_all.txt
nice -n 10 ./tagtest 32 1000 3 0 -1 0 >> tag_all.txt
nice -n 10 ./tagtest 32 1000 3 0 0 0xdcc99396 >> tag_all.txt
nice -n 10 ./tagtest 32 1000 3 1 1 0xf2ed66ff >> tag_all.txt
nice -n 10 ./tagtest 32 1000 3 2 2 0x6a6ae768 >> tag_all.txt
nice -n 10 ./tagtest 32 1000 3 3 3 0x21bade02 >> tag_all.txt
nice -n 10 ./tagtest 32 1000 3 4 4 0x07489671 >> tag_all.txt
nice -n 10 ./tagtest 32 1000 3 5 5 0x9dd8904f >> tag_all.txt
nice -n 10 ./tagtest 32 1000 3 6 6 0x63e8540e >> tag_all.txt
nice -n 10 ./tagtest 32 1000 3 7 7 0x6102dd70 >> tag_all.txt
nice -n 10 ./tagtest 32 1000 3 0 8 0x522c4f8d >> tag_all.txt
nice -n 10 ./tagtest 32 1000 3 1 9 0x466de486 >> tag_all.txt
nice -n 10 ./tagtest 32 1000 3 2 10 0x2f564652 >> tag_all.txt
nice -n 10 ./tagtest 32 1000 3 3 11 0x83faac57 >> tag_all.txt
echo finished >> tag_all.txt
