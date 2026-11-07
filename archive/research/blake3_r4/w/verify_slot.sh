
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
DST="$HOME/hashsmash/yukon/pos_b3r4/pareto"; NOTE=submission-note.md
cd "$DST" || exit 1
(cd candidates/blake3 && find . -type f -print0 | sort -z | xargs -0 sha256sum; sha256sum "../../$NOTE" | sed 's# \.\./\.\./# #') | diff -q - STAGED.sha256 >/dev/null && echo "staged files match STAGED.sha256"
echo "a6d331fdca9f18b79fab4a2f0e167254f6649fda13f38b90f37ab93437485c4a  dependencies.json" | sha256sum -c - 
ls -l .yukon/work/tracks/blake3-pareto/judge-evidence.json
cmp dependencies.json "${HASHCYBERAXE_WORKSPACE}/research/blake3_r4/b4/pkg/dependencies.json" && echo "deps match pkg"
cmp candidates/blake3/proof.md "${HASHCYBERAXE_WORKSPACE}/research/blake3_r4/b4/pkg/blake3/proof.md" && echo "proof matches pkg"
python3 -c "
import json;d=json.load(open('dependencies.json'));print(len(d),[x['submissionId'][:8] for x in d], [len(x['rationale']) for x in d])"
