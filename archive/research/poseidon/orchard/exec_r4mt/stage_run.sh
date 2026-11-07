
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
export PATH=/root/.local/bin:/root/.bun/bin:$PATH
yukon benchmark show mooselumph/hashsmash-pareto/poseidon --json | python3 -c 'import json,sys; d=json.load(sys.stdin)["benchmark"]; print(d["status"], d["submissionAdmission"])'
E="${HASHCYBERAXE_WORKSPACE}"/research/poseidon/orchard/exec_r4mt
bash "${HASHCYBERAXE_WORKSPACE}"/research/launch/slotstage/slotstage_pareto.sh POSR4M poseidon 4 $E/pkg_fin $E/submission-note_fin.md pos_posr3e
