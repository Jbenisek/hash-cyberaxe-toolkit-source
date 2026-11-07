
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
set -e
cd "${HASHCYBERAXE_WORKSPACE}/research/fifties/av11"
# args: seconds_per_q dflag tag
S=${1:-10}; DF=${2:-11}; TAG=${3:-test}
./av11 measure 00000000 $DF $S 1001 meas_${TAG}_q00000000_d${DF}.json
./av11 measure 80000000 $DF $S 2002 meas_${TAG}_q80000000_d${DF}.json
