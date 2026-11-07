
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/poseidon/certb_fast
C=12894125564123335855227378247026121035387943383342050628014288421295627833647
nice -n 10 ./certb_fast certify --F tests/data/F_j0.bin --center $C --f out/search1/c2_f.bin --cofactor out/search1/c2_cofactor.bin --outdir witness_c2 > witness_c2/certify.log 2>&1
echo rc=$? >> witness_c2/certify.log
