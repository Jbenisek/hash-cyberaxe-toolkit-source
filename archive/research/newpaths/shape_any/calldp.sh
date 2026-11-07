
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/shape_any
for p in $(ps -eo pid,args | grep "cad.sh" | grep -v grep | awk '{print $1}'); do kill $p; done
pkill -f "cadical -q r_outhalf_T2_S10.cnf"
sleep 1
gcc -O2 -o bd3 bd.c -lm 2>&1 | grep -i error
for s in fixed outhalf_kmsg outhalf_p5 fixed_p2; do
  [ -f $s.sys ] || continue
  timeout 300 ./bd3 calldp $s.sys merge > calldp_$s.txt 2>&1
  echo "calldp_$s exit=$? $(date +%T)" >> sa_runs.log
done
timeout 900 ./bd3 calldp outhalf.sys merge > calldp_outhalf.txt 2>&1
echo "calldp_outhalf exit=$? $(date +%T)" >> sa_runs.log
cd cnf
timeout 1200 cadical -q r_outhalf_T2_S10.cnf > r_outhalf_T2_S10.cadical.out 2>&1; echo "r_outhalf_T2_S10(cadical) exit=$? $(date +%T)" >> ../lb_runs.log
