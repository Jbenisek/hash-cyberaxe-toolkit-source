
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/dig/incoming/sha256-37-U02/work
T="${HASHCYBERAXE_WORKSPACE}"/research/tools/traillab
CHI=$T/chi/chi37.txt
run(){ N=$1; S=$2; R=$3; echo "== $N seeds $S relax: $R" > out_$N.txt; ( time timeout 1500 $T/traillab window --chi $CHI --rows 22 36 --event out --np 4096 --mt 1024 --threads 3 --seeds $S --prefix-relax "$R" ) >> out_$N.txt 2>&1; }
run e15z 1 "P=dropq E16 00000010 ; dropx2 E15 ; lin E15[4]^E16[4]=0"
run e15V 1,2 "P=dropq E16 00000010 ; dropx2 E15 ; lin E15[4]^E16[4]=1"
echo ALLDONE > win15.done
