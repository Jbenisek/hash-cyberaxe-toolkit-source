
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/shape_any
timeout 900 ./bdp outhalf.sys 2 20000 51 m0,m1,m2,m3,m4,m5,m6,m7,m8,m9 > ub_outhalf_kmsg_long.txt 2>&1
echo "ub_outhalf_kmsg_long exit=$? $(date +%T)" >> sa_runs.log
timeout 900 ./bdp outhalf.sys 2 20000 52 > ub_outhalf_empty_long.txt 2>&1
echo "ub_outhalf_empty_long exit=$? $(date +%T)" >> sa_runs.log
timeout 900 ./bdp outhalf.sys 2 20000 53 m8,m9,m10,m11,m12,m13,m14,m15,m0,m1 > ub_outhalf_dmsg_long.txt 2>&1
echo "ub_outhalf_dmsg_long exit=$? $(date +%T)" >> sa_runs.log
timeout 900 ./bdp fixed.sys 2 20000 54 > ub_fixed_p2_long.txt 2>&1
echo "ub_fixed_p2_long exit=$? $(date +%T)" >> sa_runs.log
