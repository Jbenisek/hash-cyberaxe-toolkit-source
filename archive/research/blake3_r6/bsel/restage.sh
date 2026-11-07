
# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
export PATH="$HOME/.local/bin:$HOME/.bun/bin:$PATH" NO_COLOR=1
W="${HASHCYBERAXE_WORKSPACE}"/research
for r in 6 7; do
 P=$W/blake3_r${r}/compact_u5b/pkg
 S=$HOME/hashsmash/yukon/pos_b3r${r}u5b/pareto
 cp -r $P/blake3/. $S/candidates/blake3/
 sed -i 's/"submission_state": "draft"/"submission_state": "ready"/' $S/candidates/blake3/claim.json
 cp $P/submission-note.md $S/submission-note.md; cp $P/dependencies.json $S/dependencies.json
 cd $S; rm -rf .yukon/work
 python3 -B ../scripts/pareto_candidate.py --family blake3 --rounds $r 2>&1 | tail -n 1
 (cd candidates/blake3 && find . -type f -not -path '*/__pycache__/*' -print0 | sort -z | xargs -0 sha256sum) > STAGED.sha256; sha256sum submission-note.md >> STAGED.sha256
 nice -n 19 python3 -B ../scripts/pareto_pipeline.py intake --family blake3 2>&1 | tail -n 2
 cat .yukon/work/tracks/blake3-pareto/pareto-outcome.json; echo
 cp .yukon/work/tracks/blake3-pareto/experiment-report.json $W/blake3_r${r}/compact_u5b/organizer_report_final.json
 sha256sum STAGED.sha256 dependencies.json | tee $W/blake3_r${r}/compact_u5b/restage.sha
 rm -rf __pycache__
done
