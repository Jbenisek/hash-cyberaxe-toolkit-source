
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}/research/poseidon/levels/U9"
( for q in 1000003 786433; do for s in 1 2 3; do python u9_toy_support.py $q $s 2 5 3126; python u9_toy_support.py $q $s 1 60 3126; done; done ) > u9_toy_support_output.txt 2>&1
