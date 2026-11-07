
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/shape_any
for p in $(ps -eo pid,args | grep "calldp.sh" | grep -v grep | awk '{print $1}'); do kill $p; done
pkill -f "cadical -q r_outhalf_T2_S10.cnf"
sleep 1
gcc -O2 -o bdp2 bdp.c -lm 2>&1 | grep -i error
P5="D1.a1,D1.b1,D1.c1,D2.a2,K0.a1,K0.b2,K0.c2,K1.b2,K1.c2,K1.d2,K2.a1,K2.b1,K2.c1,K3.a1,K3.a2,K3.b1,K3.c1,K3.d2,m0,m10,m4,m5,m6"
timeout 700 ./bdp2 outhalf.sys brickp 2 3000 101 $P5 > brickp_outhalf_p5.txt 2>&1
echo "brickp_outhalf_p5 exit=$? $(date +%T)" >> sa_runs.log
timeout 700 ./bdp2 outhalf.sys brickp 2 3000 102 m0,m1,m2,m3,m4,m5,m6,m7,m8,m9 > brickp_outhalf_kmsg.txt 2>&1
echo "brickp_outhalf_kmsg exit=$? $(date +%T)" >> sa_runs.log
timeout 400 ./bdp2 fixed.sys brickp 2 3000 103 m0,m4 > brickp_fixed.txt 2>&1
echo "brickp_fixed exit=$? $(date +%T)" >> sa_runs.log
