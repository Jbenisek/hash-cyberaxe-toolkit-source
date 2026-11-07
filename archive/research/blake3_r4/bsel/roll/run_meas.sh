
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# per-row measurements of the select roll (WSL): timing of the two experiments, --stats, appA certificate, organizer-reference regression
for r in 3 5 6 7; do
  D="${HASHCYBERAXE_WORKSPACE}/research/blake3_r$r/bsel"
  echo "=== r$r $(date +%T)"
  nice -n 10 bash "$D/tm_only.sh" 2>&1 | tail -2
  ( cd "$D/pkg/blake3/experiments" && ( time nice -n 10 python3 -B bsrho.py --stats > ../../../stats_out.txt 2>&1 ) 2> ../../../stats.time; rm -rf __pycache__ )
  ( cd "$D" && nice -n 10 python3 -B appA.py > appA.out 2> appA.err; tail -3 appA.out )
  nice -n 10 bash "$D/ext/rr.sh" 2>&1 | tail -5
done
echo DONE $(date +%T)
