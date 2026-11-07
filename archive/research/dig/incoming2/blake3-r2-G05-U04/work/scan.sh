#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/dig/incoming2/blake3-r2-G05-U04/work
gcc -O2 -o scan scan.c || exit 1
# column 2: A=IV2 B=IV6 C=IV2 ; column 3: A=IV3 B=IV7 C=IV3
S=$(date +%s)
./scan 3c6ef372 1f83d9ab 3c6ef372 55 63 12345678 9abcdef0
./scan 3c6ef372 1f83d9ab 3c6ef372 55 54 0badf00d deadbeef
./scan a54ff53a 5be0cd19 a54ff53a 11 12 12345678 9abcdef0
./scan a54ff53a 5be0cd19 a54ff53a 11 11 0badf00d deadbeef
echo "seconds: $(( $(date +%s)-S ))"
