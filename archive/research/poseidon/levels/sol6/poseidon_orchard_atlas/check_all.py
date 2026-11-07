"""Run finite research checks; never reads credentials or accesses a network."""
import subprocess,sys,time,json,csv
from pathlib import Path
B=Path(__file__).resolve().parent
if __name__=='__main__':
    start=time.perf_counter()
    for script in ['analyze.py','low_round_chart.py','build_toy.py','extra_checks.py','build_documents.py','export_grid_feed.py']:
        subprocess.run([sys.executable,str(B/script)],cwd=B,check=True)
    d=B/'data';r=json.loads((d/'results.json').read_text());l=json.loads((d/'low_round_chart_results.json').read_text())
    assert r['official_vector_checks']==14 and r['native_round_inverse_tests']==1024
    assert r['forward_grid_cells_sampled']==2080 and r['sbox_toy_exhaustive_cases']==65792
    assert l['tests']==2048 and l['two_round_degree_in_transformed_coordinates']==5
    print('ALL RECORDED CHECKS PASSED; wall_seconds=',time.perf_counter()-start)
