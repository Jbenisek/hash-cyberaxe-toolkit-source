
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
set -e
cd "${HASHCYBERAXE_WORKSPACE}/research/fifties/rates"
# mode bdom m seconds seed
./rates 1 0 8 900 11 r_spcJ_b0.json r_spcJ_b0_pass.bin r_spcJ_b0_sample.bin
./rates 2 0 8 900 12 r_spcJA_b0.json r_spcJA_b0_pass.bin r_spcJA_b0_sample.bin
./rates 0 0 8 240 10 r_ord_b0.json r_ord_b0_pass.bin r_ord_b0_sample.bin
./rates 1 1 8 360 21 r_spcJ_bq.json r_spcJ_bq_pass.bin r_spcJ_bq_sample.bin
./rates 0 1 8 120 20 r_ord_bq.json r_ord_bq_pass.bin r_ord_bq_sample.bin
echo PROD_DONE
