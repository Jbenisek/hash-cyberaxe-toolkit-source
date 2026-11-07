
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
W="${HASHCYBERAXE_WORKSPACE}"/research
for r in 6 5 4 7; do
 cd $HOME/hashsmash/yukon/pos_b3r${r}u5b/pareto || continue
 (cd candidates/blake3 && find . -type f -print0 | sort -z | xargs -0 sha256sum; sha256sum ../../submission-note.md | sed 's# \.\./\.\./# #') | diff -q - STAGED.sha256 && echo "r$r staged ok"
 grep -o '[0-9a-f]\{64\}  dependencies.json' $W/launch/submit_pareto_pos_b3r${r}u5b.sh | sha256sum -c - 2>&1 | head -n 1
 sha256sum -c <(grep -o '[0-9a-f]\{64\}  dependencies.json' $W/launch/submit_pareto_pos_b3r${r}u5b.sh) 2>&1 | head -n 1
 cmp dependencies.json $W/blake3_r${r}/compact_u5b/pkg/dependencies.json && echo deps-same
done
