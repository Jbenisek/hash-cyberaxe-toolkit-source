#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# test build at RR=1 (new nolibc code vs the old exec_r2_line libc code), outside the package
set -u
cd "${HASHCYBERAXE_WORKSPACE}"/research/poseidon/orchard/exec_r2_line2 || exit 1
mkdir -p /tmp/r2l2
CFN="-O3 -march=native -static -nostdlib -fno-stack-protector -U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=0 -fno-pie -no-pie -ffunction-sections -fdata-sections -Wl,--gc-sections -Wall -Wextra -Wno-unused-function -Wno-unused-variable -Wno-unused-parameter"
gcc $CFN -DRR=1 -DARENA=20971520 -o /tmp/r2l2/new1 single.c common.c ntt.c poly.c lean.c line.c split.c hgcd.c pallas.c nolibc.c 2> /tmp/r2l2/gcc_new.err; echo "gcc new exit $?"; head -40 /tmp/r2l2/gcc_new.err
