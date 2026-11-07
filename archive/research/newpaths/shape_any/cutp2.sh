
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/shape_any
timeout 900 ./bdp outhalf.sys cutp 2 150000 24 91 > cutp2_outhalf.txt 2>&1
echo "cutp2_outhalf exit=$? $(date +%T)" >> sa_runs.log
timeout 300 ./bdp fixed.sys cutp 4 150000 16 92 > cutp_fixed_S0.txt 2>&1
echo "cutp_fixed_S0 exit=$? $(date +%T)" >> sa_runs.log
