#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# RECOUNT agent: the program's own self-tests and my tracer, under WSL. Research only; nothing is filed.
set -u
P="${HASHCYBERAXE_WORKSPACE}/research/pkg8/program"
R="${HASHCYBERAXE_WORKSPACE}/research/pkg8/review/recount"
mkdir -p ~/hashsmash/pkg8_review
cd "$P" || exit 1
nice -n 5 python3 -B halfsearch_cluster.py --selftest 2000 1 > ~/hashsmash/pkg8_review/base.json 2>&1
echo "base selftest exit $?"
nice -n 5 python3 -B halfsearch_cluster.py --cluster-selftest 50000 pkg8 > ~/hashsmash/pkg8_review/cluster.json 2>&1
echo "cluster selftest exit $?"
python3 -c "
import json
b=json.load(open('$HOME/hashsmash/pkg8_review/base.json'))
print('base: lanes', b['lanes_right'],'/',b['lanes_checked'],'stageA',b['stage_a'] if 'stage_a' in b else '',  'registers', b.get('registers'))
c=json.load(open('$HOME/hashsmash/pkg8_review/cluster.json'))
print('cluster: trials',c['trials_checked'],'h1',c['h1_equals_tl_ref'],'k8',c['k8_equals_tl_ref'],'gate',c['gate_equals_H4_of_tl_ref'],'/',c['clusters'])
print('cluster: mixed lanes stageA',c['packed_stage_a_flag_equals_scalar'],'stage2',c['packed_stage_2_word_equals_reference'],'of',c['packed_lanes'])
print('cluster: new_counts', json.dumps(c['new_counts'],separators=(',',':')))
"
cd "$R" || exit 1
nice -n 5 python3 -B run_many.py 60 wsl60 2>&1 | head -12
