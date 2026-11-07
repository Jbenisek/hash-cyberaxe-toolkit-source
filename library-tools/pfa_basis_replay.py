"""Check the archived small-field PFA maps on zero and every basis vector.

Usage: python -B pfa_basis_replay.py /path/to/pfa_check.py
Requires Python 3.8+. No network, subprocesses, writes or large-field search.
The exact source hash is enforced before runpy executes the reviewed diagnostic.
"""
import contextlib
import hashlib
import io
from pathlib import Path
import random
import runpy
import sys

if len(sys.argv) != 2:
    raise SystemExit('Usage: python -B pfa_basis_replay.py /path/to/pfa_check.py')
source = Path(sys.argv[1])
expected_sha = 'bfe828a480c84fe49e416cda4212ab9942c34d0651c6732aa868a624487a53c6'
if hashlib.sha256(source.read_bytes()).hexdigest() != expected_sha:
    raise SystemExit('Source hash differs from the reviewed pfa_check.py; refusing to execute it.')
if not __debug__:
    raise SystemExit('Run normal Python, not -O: the replay relies on assertions.')

random.seed(0)
out = io.StringIO()
with contextlib.redirect_stdout(out):
    namespace = runpy.run_path(str(source))
expected = ['73 2 c0 2 theta order ok True layout ok True',
            '73 3 c0 1 theta order ok True layout ok True',
            '193 4 c0 2 theta order ok True layout ok True']
assert out.getvalue().splitlines() == expected
original = random.randrange
count = 0
try:
    for case, (q, a) in enumerate(((73, 2), (73, 3), (193, 4))):
        length = 3 * (1 << a)
        for index in range(-1, length):
            values = iter(int(i == index) for i in range(length))

            def draw(modulus):
                assert modulus == q
                return next(values)

            random.randrange = draw
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                namespace['test'](q, a)
            assert out.getvalue().strip() == expected[case]
            assert next(values, None) is None
            count += 1
finally:
    random.randrange = original
assert count == 87
print('PASS: 3 seeded vectors; 84 basis vectors; 3 zero vectors; all layout comparisons true')

# Proof scope: for fixed q and a, both reviewed maps are F_q-linear in x.
# Every output coordinate is a sum of fixed coefficients times input entries;
# rotations and bit reversal are fixed permutations. Equality on all basis
# vectors therefore implies equality on every vector in those three tiny fields.
# This does not verify a production-field or optimized C implementation.
