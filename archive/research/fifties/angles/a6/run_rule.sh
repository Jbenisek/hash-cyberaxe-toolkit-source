
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}/research/fifties/angles/a6"
I=$(python3 -c "
import struct
rec=open('out_random.bin','rb').read()
print(next(i for i in range(len(rec)//44) if struct.unpack_from('<4Q3I',rec,44*i)[6]>0))")
echo "check frame $I"
python3 check_frame.py frames_random.bin out_random.bin $I > check_nj.log 2>&1 &
python3 rule_dups.py frames_random.bin out_random.bin
python3 rule_dups.py frames_w6.bin out_w6.bin
wait
cat check_nj.log
