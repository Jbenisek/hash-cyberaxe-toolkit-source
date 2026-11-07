"""Finite copied-template checks; no launchers, CNF encoders or solvers are run."""
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

if not __debug__:
    raise SystemExit('Run without -O')
PUB = Path(__file__).resolve().parents[1]
ROOT = PUB.parents[1]
PINS = {
    'research/game/climber/guided/minsup/mk_tap.py': 'f8547f0ea192e61d47c5ed50e287276d0b80e17a53a05dd03c853b43482222e9',
    'research/luna/L005/shapes.tsv': 'f83cee2081ebe30a657798c2b2dfa1b275729493a82900edb44c464437011382',
    'research/luna/L002/build_sparse42_fix4.sh': '58ad605e7dd58ea3a88754c523a59dac08169184e5e5077e2cd4840543dda781',
    'research/luna/L005/run_fullstate_fix.sh': '505fc7a14b98b51ac2b6b5f9f29b846f391750ef8d23c5e1be277a755015debf',
}
raws = {path:(ROOT/path).read_bytes() for path in PINS}
for path, raw in raws.items():
    assert hashlib.sha256(raw).hexdigest() == PINS[path], path
dataset = raws['research/luna/L005/shapes.tsv'].decode('utf-8').splitlines()
assert len(dataset) == 11
cases = []
with tempfile.TemporaryDirectory(prefix='library-early-state-') as tmp:
    work = Path(tmp)
    generator = work/'mk_tap.py'
    generator.write_bytes(raws['research/game/climber/guided/minsup/mk_tap.py'])
    for line in dataset:
        name, steps, words, kicks = line.split('\t')
        n = int(steps)
        base = [int(x) for x in words.split(',')]
        extra = [int(x) for x in kicks.split(',')]
        assert base == sorted(set(base)) and all(0 <= x < 16 for x in base)
        assert all(16 <= x < n for x in extra)
        first = base[0]
        modes = {}
        for label, start in (('old',8), ('corrected',first)):
            target = work/f'{name}-{label}.xml'
            cmd = [sys.executable,'-I','-B',str(generator),str(target),str(n),words+','+kicks,f'{start}-{n-5}']
            proc = subprocess.run(cmd, cwd=work, capture_output=True, text=True, timeout=10)
            assert proc.returncode == 0 and proc.stdout == '' and proc.stderr == '', name
            text = target.read_text(encoding='utf-8')
            rows = {}
            for t, a, e, w in re.findall(r'^\s*(-?\d+) A: ([?-]{32}) E: ([?-]{32})(?: W: ([?-]{32}))?$',text,re.M):
                assert int(t) not in rows
                rows[int(t)] = (a,e,w)
            assert set(rows) == set(range(-4,n))
            for t in range(-4,n):
                a,e,w = rows[t]
                expected = '?'*32 if 0 <= t and start <= t <= n-5 else '-'*32
                assert a == e == expected, (name,label,t)
                assert w == (('?' if t in base+extra else '-')*32 if t >= 0 else '')
            assert rows[first][2] == '?'*32
            modes[label] = {'first_word_state_free':rows[first][0] == '?'*32,
                            'xml_sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
        assert modes['corrected']['first_word_state_free']
        cases.append({'shape':name,'steps':n,'first_required_word':first,
                      'old_first_difference_contradiction':first < 8,'templates':modes})

# Additive injectivity: with a common pre-step state, A' = alpha + W and
# E' = epsilon + W modulo 2^w. Exhaustive toy control illustrates the lemma;
# the word-size-independent algebraic proof is stated in the article.
toy = 0
for common in range(256):
    for delta in range(256):
        changed = (common + delta) & 255
        assert (changed == common) == (delta == 0)
        toy += 1
bad = sum(x['old_first_difference_contradiction'] for x in cases)
assert bad == 8 and len(cases)-bad == 3
assert int('9,2,11'.split(',')[0]) != min(map(int,'9,2,11'.split(',')))
report = {'passed':True,'finished_at':datetime.now(timezone.utc).isoformat(),
    'checker_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    'source_sha256':PINS['research/game/climber/guided/minsup/mk_tap.py'],
    'input_files':[{'path':path,'sha256':digest} for path,digest in PINS.items()],
    'cases':cases,'results':{'saved_shapes':11,'generated_templates':22,
        'old_first_difference_contradictions':bad,'not_excluded_by_this_obstruction':3,
        'toy_additive_injectivity_controls':toy,'unsorted_first_word_is_not_minimum':True},
    'scope':'Only copied mk_tap text generation and 8-bit additive controls were executed. Launchers were read, not run. No SAT verdict, solver certificate, 32-bit collision, cost or corrected-shape satisfiability is established.'}
(PUB/'qa/early-state-contract-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
dataset_report = {**report, 'source_sha256':PINS['research/luna/L005/shapes.tsv']}
(PUB/'qa/early-state-shapes-report.json').write_text(json.dumps(dataset_report,indent=2),encoding='utf-8')
print(json.dumps({'passed':True,**report['results'],'scope':report['scope']},indent=2))
