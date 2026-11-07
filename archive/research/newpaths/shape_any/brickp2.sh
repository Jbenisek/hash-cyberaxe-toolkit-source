
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/shape_any
until grep -q "^brickp_fixed" sa_runs.log; do sleep 3; done
for s in 111 112 113 114; do
  timeout 300 ./bdp2 outhalf.sys brickp 2 40000 $s m0,m1,m2,m3,m4,m5,m6,m7 > brickp2_outhalf_$s.txt 2>&1
  echo "brickp2_outhalf_$s exit=$? $(date +%T)" >> sa_runs.log
done
