"""Isolated source-function contracts; never import/run the campaign or a solver."""
import argparse
import ast
import hashlib
import json
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

PUB = Path(__file__).resolve().parents[1]
SOURCE = 'research/game/climber/guided/midscan/mid_driver.py'
EXPECTED = 'e295b1f64fb222d0c87e0994a92181eaa3870f560a7c39c4a93bce9418189cca'
if not __debug__:
    raise RuntimeError('Run without -O: these checks require Python assertions')
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source', type=Path, help='Exact archived mid_driver.py; read only, never imported')
args = parser.parse_args()
site = PUB if (PUB/'archive').is_dir() else PUB/'site'
raw = (args.source or site/'archive'/SOURCE).read_bytes()
assert hashlib.sha256(raw).hexdigest() == EXPECTED
tree = ast.parse(raw)
names = {'pin', 'bands', 'key', 'done_keys', 'traj', 'build'}
selected = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names]
assert {node.name for node in selected} == names
# SHA-256's first four standard constants, used only for the four-step fixture.
scope = {'json': json, 'MASK': 0xffffffff,
         'R': lambda x, k: ((x >> k) | (x << (32-k))) & 0xffffffff,
         'sha_cnf': SimpleNamespace(K=[0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5])}
exec(compile(ast.Module(body=selected, type_ignores=[]), SOURCE, 'exec'), scope)
assert scope['pin']([11, 12, 13], 5) == [11, -12, 13]
assert scope['bands'](4) == [(0, 3)]
assert len(scope['bands'](38)) == 18
assert scope['bands'](39)[-1] == (34, 37)
assert scope['key']('family', 'A2', 0, 3) == 'family|A2|0-3'

with tempfile.TemporaryDirectory(prefix='library-mid-functions-') as temporary:
    root = Path(temporary)
    results = root / 'RESULTS.tsv'
    results.write_text('# header\nfam\tA0\tmid=0-3\tctl\tUNDECIDED\t1\tsolve\n'
                       'fam\tA1\tmid=0-3\treal\tBUILDFAIL\t0\t0\n'
                       'fam\tA2\tmid=0-3\treal\tSAT_NOVERIFY\t1\tsolve\n')
    scope.update(RESULTS=str(results), os=SimpleNamespace(path=SimpleNamespace(exists=lambda p: Path(p).exists())))
    assert scope['done_keys']() == {'fam|A0|0-3', 'fam|A2|0-3'}

    mp = {}; counter = 0
    for axis in ('A', 'E'):
        for side in ('1', '2'):
            mp[axis+side] = {}; mp[axis+side+'all'] = {}
            for t in range(-4, 4):
                bits = list(range(counter+1, counter+33)); counter += 32
                mp[axis+side+'all'][str(t)] = bits
                if t < 0: mp[axis+side][str(t)] = bits
    for side in ('1', '2'):
        mp['W'+side] = []
        for word in range(16):
            mp['W'+side].append(list(range(counter+1, counter+33))); counter += 32
    cv = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
          0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19]
    other_cv = [x ^ 0x01010101 for x in cv]
    m1 = [0]*16; m2 = [1]+[0]*15
    cnf = root/'fixture.cnf'; mapping = root/'fixture.map'

    def fake_encode(xml, target, map_path):
        Path(target).write_text(f'p cnf {counter} 0\n')
        Path(map_path).write_text(json.dumps(mp))

    scope['encode'] = fake_encode
    scope['build']('fixture-only', str(cnf), str(mapping), m1, m2, cv, 4, '0-3', 'ctl')
    control = [line for line in cnf.read_text().splitlines() if line.strip()]
    assert control[0] == f'p cnf {counter} 512' and len(control[1:]) == 512
    assert all(re.fullmatch(r'-?\d+ 0', line) for line in control[1:])
    scope['build']('fixture-only', str(cnf), str(mapping), m1, m2, cv, 4, '0-3', 'real')
    real = [line for line in cnf.read_text().splitlines() if line.strip()]
    assert real[0] == f'p cnf {counter} 513' and real[1:-1] == control[1:]
    exclusion = real[-1].split()
    assert exclusion[-1] == '0' and len(exclusion[:-1]) == 1536

    # Deterministically model the legal interleaving while encode waits:
    # another worker assigns CVG after this worker sets it and before traj reads it.
    def interleaved_encode(xml, target, map_path):
        fake_encode(xml, target, map_path)
        scope['CVG'] = other_cv

    scope['encode'] = interleaved_encode
    scope['build']('fixture-only', str(cnf), str(mapping), m1, m2, cv, 4, '0-3', 'real')
    interleaved = [line for line in cnf.read_text().splitlines() if line.strip()]
    changed = sum(a != b for a, b in zip(real[1:-1], interleaved[1:-1]))
    assert changed > 0 and interleaved[-1] == real[-1]
    scope['encode'] = fake_encode
    scope['build']('fixture-only', str(cnf), str(mapping), m1, m2, other_cv, 4, '0-3', 'ctl')
    assert [line for line in cnf.read_text().splitlines() if line.strip()][1:] == interleaved[1:-1]

report = {'passed': True, 'source_sha256': EXPECTED,
          'checker_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          'finished_at': datetime.now(timezone.utc).isoformat(),
          'scope': 'Six AST-selected source functions only, synthetic four-step map and stub encoder. No module import, campaign, SAT solve or historical-run validity claim.',
          'results': {'selected_functions': sorted(names), 'control_pin_units': 512,
                      'real_exclusion_literals': 1536,
                      'interleaved_pin_units_changed': changed,
                      'resume_skips_UNDECIDED_and_SAT_NOVERIFY': True,
                      'resume_key_omits_mode': True,
                      'interleaved_exclusion_unchanged': True}}
if (PUB/'qa').is_dir():
    (PUB/'qa/mid-driver-runtime-report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
