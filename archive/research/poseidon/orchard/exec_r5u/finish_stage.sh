
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
set -e
E="${HASHCYBERAXE_WORKSPACE}"/research/poseidon/orchard/exec_r5u
S="${HASHCYBERAXE_WORKSPACE}"/research/launch/slotstage/out/submit_POSR5U.sh
D=$HOME/hashsmash/yukon/pos_posr5u/pareto
install -m 0644 $E/dependencies.json $D/dependencies.json
H=$(sha256sum $D/dependencies.json | cut -d' ' -f1)
python3 - "$S" "$H" <<'P'
import sys
s=open(sys.argv[1]).read(); h=sys.argv[2]
old='yukon submit --track poseidon --model "${MODEL:-Claude Opus 5.5}" --harness "Claude Code" --note-file "$NOTE" >'
assert old in s
new='echo "%s  dependencies.json" | sha256sum -c - >/dev/null || { echo "STOP: dependencies.json changed"; exit 1; }\nyukon submit --track poseidon --model "${MODEL:-Claude Opus 5.5}" --harness "Claude Code" --note-file "$NOTE" --dependencies-file "$DST/dependencies.json" >' % h
s=s.replace(old,new).replace('Dependencies/credit','Dependencies/credit')
s=s.replace('# THE SUBMIT of','# Dependency: 27d33f4a (POSR5T). Score 34.73775 + 12.244 = 46.98175.\n# THE SUBMIT of',1)
open(sys.argv[1],'w').write(s)
P
bash -n $S && echo syntax ok
cat $S
(cd $D && sha256sum -c STAGED.sha256 2>&1 | tail -3)
