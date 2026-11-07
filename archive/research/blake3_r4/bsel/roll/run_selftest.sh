
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
for r in 3 5 6 7; do
  E="${HASHCYBERAXE_WORKSPACE}/research/blake3_r$r/bsel/pkg/blake3/experiments"
  ( cd "$E" && ulimit -v 4000000 && nice -n 10 python3 -B bsrho.py --selftest > ../../../ext/selftest.out 2>&1; rm -rf __pycache__ )
  echo "=== r$r"; cat "$E/../../../ext/selftest.out"
done
