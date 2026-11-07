
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/shape_any
pkill -f "kissat -q lb_fixed_k40_T5"
gcc -O2 -o bd bd.c -lm 2>&1 | grep -v warning | head -5
gcc -O2 -o bdp bdp.c -lm 2>&1 | grep -v warning | head -5
gcc -O2 -o toyval toyval.c -lm 2>&1 | head -5
./bd catgd fixed.sys ../gd_best_fixed_len64.txt
echo "--- toy validation w=8"
./toyval full_fixed.txt 8 1 K0
./toyval full_fixed.txt 8 1 K1
./toyval full_fixed.txt 8 1 K0 K1
./toyval full_fixed.txt 8 1 K0 D3:a1 D3:d1
./toyval full_fixed.txt 6 1 C3
./toyval full_fixed.txt 6 2 C0
