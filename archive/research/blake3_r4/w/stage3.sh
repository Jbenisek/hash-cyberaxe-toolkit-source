
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
export PATH="$HOME/.local/bin:$HOME/.bun/bin:$PATH" NO_COLOR=1
rm -rf ~/hashsmash/yukon/pos_b3r4 ~/hashsmash/yukon/pos_b3r4t
rm -f "${HASHCYBERAXE_WORKSPACE}"/research/launch/slotstage/out/submit_B3R4.sh "${HASHCYBERAXE_WORKSPACE}"/research/launch/slotstage/out/submit_B3R4T.sh
cd historical-sources/~~Projects/~HashSmash/workspace
nice -n 10 bash research/launch/slotstage/slotstage_pareto.sh B3R4 blake3 4 research/blake3_r4/b4/pkg/blake3 research/blake3_r4/b4/pkg/submission-note.md pos_b3r3pv 2>&1 | tail -6
S=~/hashsmash/yukon/pos_b3r4/pareto
cp research/blake3_r4/b4/pkg/dependencies.json $S/dependencies.json
cd $S && git -C .. status --short | head -12
date; time nice -n 10 python3 -B ../scripts/pareto_pipeline.py intake --family blake3 2>&1 | tail -2
cat .yukon/work/tracks/blake3-pareto/pareto-outcome.json; echo
cp .yukon/work/tracks/blake3-pareto/experiment-report.json "${HASHCYBERAXE_WORKSPACE}/research/blake3_r4/b4/organizer_report_final.json"
sha256sum STAGED.sha256 dependencies.json
cat STAGED.sha256
