
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}/research/tools"
nice -n 10 python3 -B rulecheck/rulecheck.py ../blake3_r6/b8r6/pkg/blake3 2>&1 | cut -c1-260 | head -120
echo "=== prefile"
cd "${HASHCYBERAXE_WORKSPACE}/research/launch"
nice -n 10 python3 -B prefile_check.py ../blake3_r6/b8r6/pkg 2>&1 | cut -c1-220 | tail -40
