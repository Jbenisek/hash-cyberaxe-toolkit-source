#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# waits for w_run.sh, then re-runs cycle.sh with SIM_EXTENT = the run's own arena extent (cached run), copies the package and stages slot POSR3G (no submit)
D="${HASHCYBERAXE_WORKSPACE}"/research/poseidon/orchard/exec_r3t21; cd $D || exit 1
while pgrep -f "exec_r3t21/w_run.sh" >/dev/null; do sleep 60; done
EXT=$(grep -ho 'ARENA size=[0-9]* extent=[0-9]*' logs/exec_run.txt | grep -o 'extent=[0-9]*' | cut -d= -f2)
echo "extent=$EXT" > logs/finish.txt
[ -n "$EXT" ] || { echo "no extent in run log" >> logs/finish.txt; exit 1; }
NICE=10 SIM_EXTENT=$EXT bash cycle.sh > logs/cycle2_out.txt 2>&1
rm -rf pkg_stage_exec_fix; cp -a pkg_stage_exec pkg_stage_exec_fix
bash ../../../launch/slotstage/slotstage_pareto.sh POSR3G poseidon 3 $D/pkg_stage_exec_fix $D/submission-note_exec.md pos_posr3e > logs/slotstage.txt 2>&1
echo "finish done $(date -u)" >> logs/finish.txt
