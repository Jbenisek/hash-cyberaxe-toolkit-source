#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# run.sh: build, then runs A and B (independent seed/function blocks) of every job, 6 processes at nice 10; results copied to data/.
set -u
H="${HASHCYBERAXE_WORKSPACE}/research/poseidon/orchard/h1meas"
mkdir -p /root/h1meas && bash "$H/build.sh" || exit 1
cd "$H"
for RUN in A B; do
  O=/root/h1meas/out/$RUN; mkdir -p $O
  python3 -B jobs.py $RUN > $O/jobs.txt
  date +%s > $O/start
  cat $O/jobs.txt | xargs -P 6 -L 1 bash -c 'nice -n 10 /root/h1meas/h1meas "$0" "$1" "$2" "$3" "$4" "$5" "$6" "$7" "$8" "$9" "${10}" > '"$O"'/"${11}"'
  date +%s > $O/end
done
mkdir -p "$H/data"; for RUN in A B; do mkdir -p "$H/data/$RUN"; cp /root/h1meas/out/$RUN/* "$H/data/$RUN/"; done
echo DONE
