
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/shape_any
while pgrep -f "z3 -smt2 z_pc_kmsg" > /dev/null; do sleep 5; done
gcc -O2 -o bdp bdp.c -lm 2>&1 | grep -i error
timeout 900 ./bdp outhalf.sys cutp 2 40000 12 71 > cutp_outhalf.txt 2>&1
echo "cutp_outhalf exit=$? $(date +%T)" >> sa_runs.log
timeout 600 ./bdp fixed.sys cutp 2 40000 8 72 > cutp_fixed_S2.txt 2>&1
echo "cutp_fixed_S2 exit=$? $(date +%T)" >> sa_runs.log
