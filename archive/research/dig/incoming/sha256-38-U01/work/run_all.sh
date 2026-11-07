#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}/research/tools/traillab"
W="${HASHCYBERAXE_WORKSPACE}"/research/dig/incoming/sha256-38-U01/work
SEEDS=${SEEDS:-9301,9302}
for f in $W/chi/*.txt; do
  n=$(basename $f .txt)
  [ -s $W/out/$n.txt ] && grep -q "^exit" $W/out/$n.txt && continue
  timeout 600 ./traillab window --chi $f --rows 22 37 --event out --no-elist --autolist --np 4096 --mt 8192 --threads 3 --seeds $SEEDS > $W/out/$n.txt 2>&1
  echo "exit $?" >> $W/out/$n.txt
done
echo ALLDONE > $W/out/_done.txt
