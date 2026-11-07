
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}/research/poseidon/orchard/single_r1_exec4"
mkdir -p /root/b4
gcc -O3 -march=native -static -Wall -Wextra -Wno-unused-function -Wno-unused-variable -Wno-unused-parameter -o /root/b4/single single.c common.c ntt.c poly.c lean.c line.c split.c hgcd.c pallas.c -lm 2>&1 | head -40
size /root/b4/single