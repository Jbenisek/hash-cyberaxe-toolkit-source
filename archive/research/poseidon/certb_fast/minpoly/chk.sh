
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/poseidon/certb_fast
head -3 tests/t_basic.py >/dev/null
for py in python3 ~/venv/bin/python3 /usr/bin/python3; do $py -c "import flint,sys;print(sys.executable,flint.__version__)" 2>&1|tail -1; done
ls ~ | grep -i -E "venv|env"
