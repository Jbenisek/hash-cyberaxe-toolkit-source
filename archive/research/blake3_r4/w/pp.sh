cd ~/hashsmash/yukon/pos_b3r3pv
python3 -B scripts/pareto_pipeline.py --help 2>&1 | head -30
sed -n 1,60p scripts/pareto_pipeline.py
