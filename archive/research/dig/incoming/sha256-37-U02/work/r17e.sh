
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/dig/incoming/sha256-37-U02/work
T="${HASHCYBERAXE_WORKSPACE}"/research/tools/traillab
R="P=dropx2 A17 ; lin A15[29]^A17[29]=0 ; lin A17[29]^A18[29]=1"
echo "== r17_e2 seeds 1,2 np 4096 mt 1024 relax: $R" > out_r17_e2.txt
$T/traillab window --chi $T/chi/chi37.txt --rows 22 36 --event out --np 4096 --mt 1024 --threads 3 --seeds 1,2 --prefix-relax "$R" >> out_r17_e2.txt 2>&1
R="P=dropx2 A17 ; lin A15[29]^A17[29]=0 ; lin A17[29]^A18[29]=0"
echo "== r17_e0 control seeds 1 relax: $R" > out_r17_e0.txt
$T/traillab window --chi $T/chi/chi37.txt --rows 22 36 --event out --np 4096 --mt 1024 --threads 3 --seeds 1 --prefix-relax "$R" >> out_r17_e0.txt 2>&1
