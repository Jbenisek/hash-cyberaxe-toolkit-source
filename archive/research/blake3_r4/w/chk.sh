
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}/research/blake3_r4/b4"
python3 -B pkg/blake3/experiments/bsrho.py --gen-c > /tmp/gen_shipped.c 2>/dev/null
diff <(cat gen_c/gen.c) /tmp/gen_shipped.c && echo "GEN_C in bsrho.py == gen_c/gen.c"
sha256sum pkg/blake3/experiments/bsrho.py ~/hashsmash/yukon/pos_b3r4t/pareto/candidates/blake3/experiments/bsrho.py
cd pkg/blake3/experiments && ( ulimit -v 2000000; nice -n 10 python3 -B bsrho.py --ledger 2>&1 | grep -v "^{" | head -30 )
