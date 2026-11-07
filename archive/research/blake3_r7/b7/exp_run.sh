
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}/research/blake3_r7/b7"
date
bash tm_run.sh
date
( ulimit -v 2000000; cd pkg/blake3/experiments; nice -n 10 python3 -B bsrho.py --stats > ../../../stats_out.txt 2>&1 ); cut -c1-200 stats_out.txt
date
