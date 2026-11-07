#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# probe_cms.sh - why the quiet CMS command failed in e3sat_time.py, and which C API symbols the library exports
D="${HASHCYBERAXE_WORKSPACE}"/research/newpaths/untried/ctr_alg
F="$D/cnf/rec11_s000_t4.xnf"
echo "== --verb 0 --printsol 0"; cryptominisat5 --maxtime 300 --verb 0 --printsol 0 "$F" 2>&1 | head -n 5; echo "rc ${PIPESTATUS[0]}"
echo "== --verb 0"; cryptominisat5 --maxtime 300 --verb 0 "$F" 2>&1 | head -n 5; echo "rc ${PIPESTATUS[0]}"
echo "== symbols"; nm -D --defined-only /usr/lib/x86_64-linux-gnu/libcryptominisat5.so.5.11 2>/dev/null | grep -oE 'cmsat_[a-z_]+' | sort -u | tr '\n' ' '; echo
