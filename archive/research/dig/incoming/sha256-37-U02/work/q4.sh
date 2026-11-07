
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
while [ ! -f win15.done ]; do sleep 20; done
run(){ N=$1; S=$2; NP=$3; MT=$4; R=$5; echo "== $N seeds $S np $NP mt $MT relax: $R" > out_$N.txt; ( time timeout 600 $T/traillab window --chi $CHI --rows 22 36 --event out --np $NP --mt $MT --threads 3 --seeds $S --prefix-relax "$R" ) >> out_$N.txt 2>&1; }
run q4ctl 1 4096 1024 "P=sym E17 =0=====+01===u1=+==0==1===1u===="
run q4_a1 1,2 4096 1024 "P=sym E17 =0=====+01===u1=+==0==1===un===="
run q4_a2 1,2 4096 1024 "P=sym E17 =0=====+01==un1=+==0==1===1u===="
run q4_a3 1,2 4096 1024 "P=sym E17 =0=====+01===u1=+==0==1==unn===="
run q4_a4 1,2 4096 1024 "P=sym E17 =0=====+01==un1=+==0==1===un===="
run q4_a5 1,2 4096 1024 "P=sym E17 =0=====+01=unn1=+==0==1===1u===="
run q4_a6 1,2 4096 1024 "P=sym E17 =0=====+01===u1=+==0==1=unnn===="
run q4_a7 1,2 4096 1024 "P=sym E17 =0=====+01==un1=+==0==1==unn===="
run q4_a8 1,2 4096 1024 "P=sym E17 =0=====+01=unn1=+==0==1===un===="
run q4_a9 1,2 4096 1024 "P=sym E17 =0=====+01unnn1=+==0==1===1u===="
run q4_a10 1,2 4096 1024 "P=sym E17 =0=====+01===u1=+==0==1unnnn===="
run q4_a11 1,2 4096 1024 "P=sym E17 =0=====+01==un1=+==0==1=unnn===="
run q4_a12 1,2 4096 1024 "P=sym E17 =0=====+01=unn1=+==0==1==unn===="
run q4_a13 1,2 4096 1024 "P=sym E17 =0=====+01unnn1=+==0==1===un===="
run q4_a14 1,2 4096 1024 "P=sym E17 =0=====+0unnnn1=+==0==1===1u===="
run r17_a 1,2 4096 1024 "P=dropx2 E17 ; lin E17[0]^E17[13]=0"
run r17_b 1,2 4096 1024 "P=dropq E17 01000000 ; dropx2 E17 ; lin E17[0]^E17[13]=1 ; lin E16[15]^E17[15]=0 ; lin E16[24]^E17[24]=1"
run r17_c 1,2 4096 1024 "P=dropq E17 00008000 ; dropx2 E17 ; lin E17[0]^E17[13]=1 ; lin E16[24]^E17[24]=0 ; lin E16[15]^E17[15]=1"
run r17_d 1,2 4096 1024 "P=dropx2 A15 ; lin A15[15]^A16[15]=1 ; lin A15[23]^A16[23]=0 ; lin A15[25]^A16[25]=0 ; lin A15[29]^A17[29]=1"
run r17_e 1,2 4096 1024 "P=dropx2 A17 ; lin A17[29]^A18[29]=1"
echo ALLDONE > q4.done
