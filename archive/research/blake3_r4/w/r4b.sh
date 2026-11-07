cd ~/hashsmash/yukon/pos_b3r3pv/pareto
cat benchmark.json | head -120
echo ------
wc -l scoring.py targets.py; grep -n "blake3\|reference_operation\|round" scoring.py | head -60
ls ../cost-models; ls scoring-policies
