
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/shape_any
for p in $(ps -eo pid,args | grep "cutp.sh" | grep -v grep | awk '{print $1}'); do kill $p; done
pkill -f "bdp fixed.sys cutp"
sleep 1
P5="D1.a1,D1.b1,D1.c1,D2.a2,K0.a1,K0.b2,K0.c2,K1.b2,K1.c2,K1.d2,K2.a1,K2.b1,K2.c1,K3.a1,K3.a2,K3.b1,K3.c1,K3.d2,m0,m10,m4,m5,m6"
timeout 600 ./bdp outhalf.sys 2 15000 81 $P5 > ub_outhalf_p5.txt 2>&1
echo "ub_outhalf_p5 exit=$? $(date +%T)" >> sa_runs.log
python3 export.py outhalf outhalf_p5.sys $P5 > /dev/null
timeout 600 ./bd sa outhalf_p5.sys 30000 3 82 > sa_outhalf_p5.txt 2>&1
echo "sa_outhalf_p5 exit=$? $(date +%T)" >> sa_runs.log
timeout 400 ./bdp fixed.sys 2 15000 83 m0,m4 > ub_fixed_p2.txt 2>&1
echo "ub_fixed_p2 exit=$? $(date +%T)" >> sa_runs.log
