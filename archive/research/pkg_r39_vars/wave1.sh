#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# wave1.sh : ledgers for the two best pairs (s108 on the published characteristic, 7111e7edc4), 11 PC + 13 cloud windows each, all at once.
B="${HASHCYBERAXE_WORKSPACE}"/research/pkg_r39_vars
for SIG in p_p39chars108_p39s 7111e7edc4; do bash $B/led_pair.sh $SIG 12 24 cloud; done
for SIG in p_p39chars108_p39s 7111e7edc4; do bash $B/led_pair.sh $SIG 1 11 pc & done
wait; bash $B/led_fetch.sh p_p39chars108_p39s 7111e7edc4
