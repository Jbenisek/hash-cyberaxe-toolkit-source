#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# pinctr.sh LENXOR DELTA|free TOP0 CTRBOUND MAXK SEED TIMEOUT
# One run of trailmin5_ctr.py (the night's pin solver with the COUNTER objective: cost without A1 = k), new pins
# only: every (D3, D11) already found for this length XOR is excluded (the night's trail5_lx.log, the server's
# trail5_server.log, pins.tsv, and the pins found here: pinctr.log; all read-only). kissat-sat with --time=TIMEOUT;
# its temporary CNF goes to scratch/tmp of this folder (TMPDIR). One process, nice 5.
# Output: scratch/pinctr_LX_SEED.out, appended to pinctr.log at the end (two runs that appended to pinctr.log at
# the same moment lost a line on mounted research volume, so each run now writes its own file first).
export PYTHONDONTWRITEBYTECODE=1
D="${HASHCYBERAXE_WORKSPACE}/research/newpaths/untried/const_alg"
N="${HASHCYBERAXE_WORKSPACE}/research/night/main/trail5_lx.log"
S="${HASHCYBERAXE_WORKSPACE}/astra-jobs/~archvie/server_tasks_2026-10-06/HashSmash_Opus_Handoff_2026-10-06_updated/server_tasks_2026-10-06/task1_pins/out/trail5_server.log"
T="${HASHCYBERAXE_WORKSPACE}/research/paths/pins.tsv"
lx=$1; delta=$2; top0=$3; b=$4; mk=$5; seed=$6; to=$7
mkdir -p "$D/scratch/tmp"
X="$D/scratch/exclude_lx${lx}_s$seed.txt"
O="$D/scratch/pinctr_lx${lx}_s$seed.out"
{ grep -h "pin-lx$lx .*status=SATISFIABLE" "$N" "$S" 2>/dev/null | sed -E 's/.* D3=([0-9a-f]+) D11=([0-9a-f]+).*/\1 \2/'
  grep -h "pinctr-lx$lx .*status=SATISFIABLE" "$D/pinctr.log" 2>/dev/null | sed -E 's/.* D3=([0-9a-f]+) D11=([0-9a-f]+).*/\1 \2/'
  awk -v lx="$lx" -F'\t' '$2 == lx {print $9, $10}' "$T"
} | sort -u > "$X"
echo "$(date +%H:%M:%S) pinctr lx$lx delta $delta top0 $top0 ctrbound $b maxk $mk seed $seed timeout $to: excluding $(wc -l < "$X") known (D3, D11), pid $$" > "$O"
d=""; [ "$delta" != "free" ] && d="--delta $delta"
TMPDIR="$D/scratch/tmp" nice -n 5 python3 -B "$D/trailmin5_ctr.py" --bound "$b" --max-k "$mk" --exclude "$X" --timeout "$to" \
  --seed "$seed" --solver kissat-sat --lenxor "$lx" $d --w13-top0 "$top0" >> "$O" 2>> "$D/run.err"
echo "$(date +%H:%M:%S) pinctr lx$lx seed $seed finished" >> "$O"
cat "$O" >> "$D/pinctr.log"
