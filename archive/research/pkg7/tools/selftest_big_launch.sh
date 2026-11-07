#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
echo "STOP: copy of a script of research/pkg6 inside research/pkg7; it still points at research/pkg6, which is filed and read only. Not ported yet (PROGRAM_STEP.md, section 6 item 1)."; exit 9
# State of the long self-test runs of tools/selftest_big.sh, and a way to stop them. Research helper, not submitted.
#
#   wsl -d Ubuntu -- bash './research/pkg6/tools/selftest_big_launch.sh' status
#   wsl -d Ubuntu -- bash './research/pkg6/tools/selftest_big_launch.sh' stop
#
# How the runs of 2026-10-06 were started: a run of 1,000,000 batches takes about half an hour per rule, and on
# this machine the processes of a "wsl ... &" end when the wsl client that started them ends (setsid and nohup did
# not keep them). They were started from PowerShell as a process of their own:
#   Start-Process -FilePath wsl.exe -WindowStyle Hidden -ArgumentList '-d','Ubuntu','--','bash',
#     './research/pkg6/tools/selftest_big.sh','1000000','61','4','5','6'
# A run that is stopped leaves an evidence file whose first line ends with "exit 143"; such a file is not evidence
# (tools/rule_figures.py and the data module use a file only with "exit 0").
set -uo pipefail
PKG="${HASHCYBERAXE_WORKSPACE}/research/pkg6"
TMP="$HOME/hashsmash/pkg6-selftest"
case "${1:-status}" in
  status)
    echo "self-test processes running: $(pgrep -f "$TMP/halfsearch_" | wc -l)"
    ls -1 "$PKG/evidence" | grep '^selftest_.*_rule' | while read -r f; do
      echo "$f: $(head -1 "$PKG/evidence/$f" | cut -c1-40) ... $(head -1 "$PKG/evidence/$f" | sed 's/.* exit/exit/')"
    done ;;
  stop)
    pkill -f "$TMP/halfsearch_"; echo "stopped: $?" ;;
  *) echo "usage: selftest_big_launch.sh status | stop"; exit 2 ;;
esac
