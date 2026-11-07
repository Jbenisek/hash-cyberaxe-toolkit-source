#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}/research/newpaths" || exit 2
for k in 5 6; do
  f="gd_fixedT_len64_k${k}_T100.cnf"
  o="tablesk${k}.out"
  echo "START k=${k} $(date +%T) file=${f}"
  /usr/bin/timeout 540 kissat -q "${f}" > "${o}" 2>/dev/null
  rc=$?
  echo "DONE k=${k} exit=${rc} $(date +%T) -> $(head -1 ${o})"
done
echo ALLDONE
