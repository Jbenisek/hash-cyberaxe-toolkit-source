
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
set -e
SLOT="$HOME/hashsmash/yukon/b3r3bs_pkg"
SRC="${HASHCYBERAXE_WORKSPACE}/research/blake3_r3/bitslice/pkg"
[ -d "$SLOT" ] || cp -a "$HOME/hashsmash/yukon/b3r3s_pkg" "$SLOT"
D="$SLOT/pareto"
rm -rf "$D/candidates/blake3"; mkdir -p "$D/candidates/blake3"
cp -r "$SRC/blake3/." "$D/candidates/blake3/"
cp "$SRC/submission-note.md" "$SRC/dependencies.json" "$D/"
cd "$D"
(cd candidates/blake3 && find . -type f -print0 | sort -z | xargs -0 sha256sum; sha256sum "../../submission-note.md" | sed 's# \.\./\.\./# #') > STAGED.sha256
find candidates/blake3 -type f -exec chmod 644 {} +; chmod 644 submission-note.md dependencies.json
cat STAGED.sha256
cd "$SLOT"
python3 scripts/pareto_candidate.py --family blake3 --rounds 3 2>&1 | tail -30
