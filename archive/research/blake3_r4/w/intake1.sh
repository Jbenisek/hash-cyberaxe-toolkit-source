export PATH="$HOME/.local/bin:$HOME/.bun/bin:$PATH" NO_COLOR=1
cd ~/hashsmash/yukon/pos_b3r4t/pareto
rm -f dependencies.json
date
time nice -n 10 python3 -B ../scripts/pareto_pipeline.py intake --family blake3 2>&1 | tail -20
echo rc=$?
cat .yukon/work/tracks/blake3-pareto/pareto-outcome.json; echo
ls -l .yukon/work/tracks/blake3-pareto/
date
