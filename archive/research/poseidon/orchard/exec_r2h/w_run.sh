
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
mkdir -p /root/b4r2
cd "${HASHCYBERAXE_WORKSPACE}/research/poseidon/orchard/exec_r2h"
gcc -O3 -march=native -static -Wall -Wextra -Wno-unused-function -Wno-unused-variable -Wno-unused-parameter -o /root/b4r2/single single.c common.c ntt.c poly.c lean.c line.c split.c hgcd.c pallas.c -lm 2>&1 | head -20
cd /root/b4r2
( ulimit -s 64; nice -n 19 /usr/bin/time -v -o /root/b4r2/time.txt ./single 1 > /root/b4r2/run.txt 2>&1; echo "EXIT $?" >> /root/b4r2/run.txt )
