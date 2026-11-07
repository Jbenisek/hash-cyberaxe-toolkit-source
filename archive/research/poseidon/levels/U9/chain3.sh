
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}/research/poseidon/levels/U9"
python u9_lc_formula.py > u9_lc_formula_output.txt 2>&1
python u9_support.py AB 2 5 3126 verify > u9_support_AB_r2_R5_output.txt 2>&1
python u9_support.py AB 1 60 3126 verify > u9_support_AB_r1_R60_output.txt 2>&1
python u9_lines_exact.py 2 102 7200 > u9_lines_exact_r2_s102_output.txt 2>&1
python u9_lines_ab.py 1 11 > u9_lines_ab_r1_s11_output.txt 2>&1
python u9_lines_ab.py 1 12 > u9_lines_ab_r1_s12_output.txt 2>&1
python u9_lines_ab.py 1 13 > u9_lines_ab_r1_s13_output.txt 2>&1
python u9_lines_ab.py 2 14 > u9_lines_ab_r2_s14_output.txt 2>&1
