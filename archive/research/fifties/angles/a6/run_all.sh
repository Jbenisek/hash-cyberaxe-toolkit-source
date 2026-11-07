
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}/research/fifties/angles/a6"
python3 check_frame.py frames_random.bin out_time.bin 0 > check0.log 2>&1 &
PY=$!
for m in control random w6; do
  ./table_hash frames_$m.bin out_$m.bin 2>/dev/null
  python3 count_dups.py frames_$m.bin out_$m.bin
done
wait $PY
cat check0.log
