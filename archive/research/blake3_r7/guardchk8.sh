
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
for s in pos_b3r6d pos_b3r5c; do
  bash -n "${HASHCYBERAXE_WORKSPACE}"/research/launch/submit_pareto_$s.sh && echo "$s syntax ok"
  cd ~/hashsmash/yukon/$s/pareto || exit 1
  (cd candidates/blake3 && find . -type f -print0 | sort -z | xargs -0 sha256sum; sha256sum "../../submission-note.md" | sed 's# \.\./\.\./# #') | diff -q - STAGED.sha256 && echo "$s staged hash ok"
  grep -c . dependencies.json; ls
  diff -rq candidates/blake3 "${HASHCYBERAXE_WORKSPACE}"/research/blake3_r${s: -2:1}/b8r${s: -2:1}/pkg/blake3 && echo "$s slot == research pkg"
  diff -q submission-note.md "${HASHCYBERAXE_WORKSPACE}"/research/blake3_r${s: -2:1}/b8r${s: -2:1}/pkg/submission-note.md && echo note same
done
