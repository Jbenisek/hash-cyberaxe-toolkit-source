
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# native x86-64 generator check per row (WSL): build, run under prlimit --data 2^20, compare with the Python reference, bisect the address-space cap; writes native.json
for r in 3 5 6 7; do
  N="${HASHCYBERAXE_WORKSPACE}/research/blake3_r$r/bsel/gen_c/native"
  out=$(nice -n 10 bash "$N/nat_all.sh" 2>&1)
  echo "=== r$r"; echo "$out" | tail -6
  sz=$(size "$N/gen_native" | tail -1)
  python3 - "$N" "$sz" "$out" <<'PY'
import sys, json, re
N, sz, out = sys.argv[1], sys.argv[2].split(), sys.argv[3]
text, data, bss = int(sz[0]), int(sz[1]), int(sz[2])
m = re.search(r"ok=(\d+) fail=(\d+)", out)
ident = "program sha256 equal to the Python reference: True ref lines equal: True" in out and "err 0" in out
d = {"identical": ident, "bss": bss, "text": text, "as_ok": int(m.group(1)), "as_fail": int(m.group(2)), "data_cap": 1048576}
json.dump(d, open(N + "/native.json", "w")); print(d)
PY
done
