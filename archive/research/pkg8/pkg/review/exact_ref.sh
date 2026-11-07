#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# exact lens: my BLAKE3 against published digests and against the organizer's reference (scratch copy).
cd "${HASHCYBERAXE_WORKSPACE}/research/pkg7/review" || exit 1
nice -n 5 python3 -B exact_blake3.py /root/hashsmash/exact_review 2>&1 | tail -8
echo "exit $?"
