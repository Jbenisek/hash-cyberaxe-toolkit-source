#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# Replicate stream (pre-registered in prereg.json): 2^28 real and 2^28 control pairs, new seeds.
cd "${HASHCYBERAXE_WORKSPACE}/research/fifties/perspectives/onescomp" || exit 1
./oc_stream real stream2_real_2p28.bin 268435456 0x4F4E45535332524C 4 > stream2_real_out.txt 2>&1 &
P1=$!
./oc_stream ctrl stream2_ctrl_2p28.bin 268435456 0x4F4E455353324354 4 > stream2_ctrl_out.txt 2>&1 &
P2=$!
wait $P1; echo "real exit $?" >> stream2_real_out.txt
wait $P2; echo "ctrl exit $?" >> stream2_ctrl_out.txt
date >> stream2_real_out.txt
