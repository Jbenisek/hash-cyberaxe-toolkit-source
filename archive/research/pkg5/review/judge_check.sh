#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# hostile-judge lens: the package's own second program, output to a file in review/ (one thread)
cd "${HASHCYBERAXE_WORKSPACE}/research/pkg5" || exit 1
start=$(date +%s)
nice -n 10 python3 -B check_pkg5.py > review/judge_check_pkg5.out 2> review/judge_check_pkg5.err
echo "exit $? seconds $(( $(date +%s) - start ))"
echo "ok lines $(grep -c '\[ok\]' review/judge_check_pkg5.out) FAIL lines $(grep -c 'FAIL' review/judge_check_pkg5.out)"
tail -n 1 review/judge_check_pkg5.out | cut -c1-200
grep -E 'organizer reference|rule A: ' review/judge_check_pkg5.out | head -3 | cut -c1-220
