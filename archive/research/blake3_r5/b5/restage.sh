
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# usage: bash restage.sh <full uuid of our filed B3R6 entry>   (WSL; run after the owner has filed r6). Rebuilds the r5 package with the real id, restages pos_b3r5, runs intake + rulecheck, writes launch/submit_pareto_b3r5.sh
set -e
U="$1"; case "$U" in ????????-????-????-????-????????????) ;; *) echo "need a full uuid"; exit 2;; esac
W="${HASHCYBERAXE_WORKSPACE}"/research
cd $W/blake3_r5/b5
sed -i "s/R6IDPLACEHOLDER-0000-0000-0000-000000000000/$U/g" proof_t.md note_t.md build_all.py
echo "$U" > $W/blake3_r6/b6/id.txt
rm -rf ~/hashsmash/yukon/pos_b3r5; rm -f $W/launch/slotstage/out/submit_B3R5.sh
bash bld.sh > bld.out 2>&1; tail -1 bld.out
cd $W/..; bash research/blake3_r5/b5/stage_run.sh > research/blake3_r5/b5/stage_run.out 2>&1; grep -E "rc=|intake|STAGED|dependencies" research/blake3_r5/b5/stage_run.out | cut -c1-120
cd $W/blake3_r5/b5; bash rc_run.sh > rc_run.out 2>&1; grep -E "mem-gate|SUMMARY|FAIL|R21" rc_run.out | cut -c1-120
DEP=$(sha256sum ~/hashsmash/yukon/pos_b3r5/pareto/dependencies.json | cut -c1-64)
sed "s/@@DEPSHA@@/$DEP/; s/@@R6ID8@@/${U:0:8}/g" submit_template.sh > $W/launch/submit_pareto_b3r5.sh; chmod +x $W/launch/submit_pareto_b3r5.sh
echo "submit script written (NOT run): launch/submit_pareto_b3r5.sh"
