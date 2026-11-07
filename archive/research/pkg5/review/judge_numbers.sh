#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}/research/pkg5/review" || exit 1
python3 -B judge_numbers.py 2>&1 | cut -c1-300 | tail -5
# the self-test quoted in the text (one thread, a few seconds); its JSON line goes to a file
cd "${HASHCYBERAXE_WORKSPACE}/research/pkg5/blake3-r2" || exit 1
python3 -B -s experiments/halfsearch.py --selftest 2000 1 > ../review/judge_selftest_2000_1.json 2> ../review/judge_selftest_2000_1.err
echo "selftest exit $? bytes $(wc -c < ../review/judge_selftest_2000_1.json)"
