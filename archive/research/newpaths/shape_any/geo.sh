
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/shape_any
while pgrep -f "z3 -smt2 z_pc_kmsg" > /dev/null; do sleep 2; done
gcc -O2 -o bd2 bd.c -lm 2>&1 | grep -i error
for sysn in fixed outhalf kmsg; do
  case $sysn in fixed) s=fixed.sys;; outhalf) s=outhalf.sys;; kmsg) s=outhalf_kmsg.sys;; esac
  for o in forward backward onion cylinder torus ring8 hexagon msgcyc star random0 random1 random2; do
    ./bd2 order $s geo_$sysn/$o.ord | grep "^order"
  done
done > geo_results.txt 2>&1
echo "geo exit=$? $(date +%T)" >> sa_runs.log
