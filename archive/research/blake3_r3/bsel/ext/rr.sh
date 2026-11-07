
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
V=$(dirname $(dirname $(ls -d /root/hashsmash/*/verifier/blake3.py /root/hashsmash/*/*/verifier/blake3.py 2>/dev/null | head -1)))
echo "verifier root: $V"
cd "${HASHCYBERAXE_WORKSPACE}/research/blake3_r3/bsel"
export PYTHONDONTWRITEBYTECODE=1
time nice -n 10 python3 -B ext/ref_regress.py "$V" pkg/blake3/experiments > ext/ref_regress.out 2>&1
cat ext/ref_regress.out
rm -rf pkg/blake3/experiments/__pycache__
