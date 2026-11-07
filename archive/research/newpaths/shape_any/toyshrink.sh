
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/shape_any
./bd shrink fixed.sys 300000 5 > shrink_fixed.txt 2>&1
head -12 shrink_fixed.txt
echo "--- toy counts at w=6 (first clusters)"
grep "^dim" shrink_fixed.txt | head -5 | while read -r line; do
  eqs=$(echo "$line" | cut -d: -f2- | sed 's/^ //')
  # equation names contain ':' (K0:a1); re-split the list after the first ' : '
  eqs=$(echo "$line" | sed 's/^dim [0-9]* rho [0-9]* : //')
  echo "$line"
  timeout 100 ./toyval full_fixed.txt 6 3 $eqs
done
