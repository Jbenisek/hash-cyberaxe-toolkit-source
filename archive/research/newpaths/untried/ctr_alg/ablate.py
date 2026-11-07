#!/usr/bin/env python3
"""ablate.py (untried/ctr_alg; research only) - which kissat technique refutes the real E3 systems with 0 conflicts?
Runs kissat (--check=0) with groups of techniques off on the main-sample CNFs (cnf/rec11_s0*.cnf, 25 real systems)
and prints, per config: systems refuted with 0 conflicts, mean conflicts / decisions / propagations, and the counters
that produced units or equivalences (summed).  One solver process at a time."""
import glob, os, re, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
STAT = re.compile(r'^c\s+([A-Za-z][\w\-]*?)\s*:\s+(\d+)')
CONFIGS = {
    'default': [],
    'no-congruence': ['--congruence=false'],
    'no-congr,no-backbone': ['--congruence=false', '--backbone=0', '--preprocessbackbone=false'],
    'no-congr,no-preprobe': ['--congruence=false', '--preprocessprobe=false'],
    'no-preprocess': ['--preprocess=false'],
    'no-congr,no-preprocess': ['--congruence=false', '--preprocess=false'],
    'plain': ['--plain'],
}
files = sorted(glob.glob(os.path.join(HERE, 'cnf', 'rec11_s0*.cnf')))
print(f'{len(files)} real systems (main sample)')
for name, opts in CONFIGS.items():
    zero = 0; tot = {'conflicts': 0, 'decisions': 0, 'propagations': 0}; units = {}
    for f in files:
        out = subprocess.run(['kissat', '--time=60', '--check=0', '-s', '-n'] + opts + [f],
                             capture_output=True, text=True).stdout
        assert 's UNSATISFIABLE' in out, (name, f)
        st = {m.group(1): int(m.group(2)) for m in map(STAT.match, out.splitlines()) if m}
        zero += st.get('conflicts', 0) == 0
        for k in tot: tot[k] += st.get(k, 0)
        for k, v in st.items():
            if v and (k.endswith('_units') or k in ('units', 'failed', 'substituted', 'backbone_units')):
                units[k] = units.get(k, 0) + v
    n = len(files)
    print(f'{name:24s} zero-conflict {zero}/{n}; mean conflicts {tot["conflicts"] / n:.1f}, decisions '
          f'{tot["decisions"] / n:.1f}, propagations {tot["propagations"] / n:.0f}; unit sources (sum): '
          + ', '.join(f'{k} {v}' for k, v in sorted(units.items())))
