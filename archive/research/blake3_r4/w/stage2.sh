export PATH="$HOME/.local/bin:$HOME/.bun/bin:$PATH" NO_COLOR=1
cd historical-sources/~~Projects/~HashSmash/workspace
nice -n 10 bash research/launch/slotstage/slotstage_pareto.sh B3R4 blake3 4 research/blake3_r4/b4/pkg/blake3 research/blake3_r4/b4/pkg/submission-note.md 2>&1 | tail -8
S=~/hashsmash/yukon/pos_b3r4/pareto
cp research/blake3_r4/b4/pkg/dependencies.json $S/dependencies.json
cd $S && ls; git -C .. status --short | head
date; time nice -n 10 python3 -B ../scripts/pareto_pipeline.py intake --family blake3 2>&1 | tail -3
cat .yukon/work/tracks/blake3-pareto/pareto-outcome.json; echo
ls -l .yukon/work/tracks/blake3-pareto/
cmp .yukon/work/tracks/blake3-pareto/experiment-report.json ~/hashsmash/yukon/pos_b3r4t/pareto/.yukon/work/tracks/blake3-pareto/experiment-report.json && echo "experiment report identical to the test slot's"
sha256sum STAGED.sha256 dependencies.json
cat STAGED.sha256
