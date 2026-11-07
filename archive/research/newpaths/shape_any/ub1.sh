
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/shape_any
gcc -O2 -o bd bd.c -lm 2>&1 | grep -i error
gcc -O2 -o bdp bdp.c -lm 2>&1 | grep -i error
# start 1: fixed-like (E0, E2 inputs) + m0, m4  (slack 10)
timeout 1200 ./bdp outhalf.sys 2 1500 41 C0.a2,C1.b2,C2.c2,C3.d2,C2.a2,C3.b2,C0.c2,C1.d2,m1,m11,m9,m14,m0,m4 > ub_outhalf_fixedlike.txt 2>&1
echo "ub_outhalf_fixedlike exit=$? $(date +%T)" >> sa_runs.log
# start 2: all round-0 column messages + D0 messages (four D blocks -> three)
timeout 1200 ./bdp outhalf.sys 2 1500 42 m0,m1,m2,m3,m4,m5,m6,m7,m8,m9 > ub_outhalf_kmsg.txt 2>&1
echo "ub_outhalf_kmsg exit=$? $(date +%T)" >> sa_runs.log
