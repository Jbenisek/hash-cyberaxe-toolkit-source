#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/dig/incoming/blake3-r2-U02/work
python3 -B cc_cell.py 8127c181,7af77f38 8124c181,7af77f38 8126c181,7af77f38 8125c181,7af77f38 8120c181,7af77f38 8123c181,7af77f38 8121c181,7af77f38 8122c181,7af77f38 8127c181,7af77f3c > cc_out.jsonl 2> cc_err.txt
echo done >> cc_err.txt
