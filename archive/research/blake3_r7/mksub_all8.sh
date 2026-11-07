
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/blake3_r7
python3 -B mkroll8_submit.py 6 pos_b3r6d B3R6c 57174971 "125.03893 (57174971)"
python3 -B mkroll8_submit.py 5 pos_b3r5c B3R5c 4a9f31b8 "125.00951 (4a9f31b8)"
