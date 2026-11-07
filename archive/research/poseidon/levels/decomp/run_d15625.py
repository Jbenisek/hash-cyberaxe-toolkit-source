"""Research-only Poseidon r2 decomposition screen for the remaining d=15625 cell."""
from decomp import *
import time

r = 2
j = 0
d = 15625
n = 5 ** (6 + r)
L = Line(j)
s0 = s0_line(L)
print(f"START r={r} j={j} d={d} n={n}", flush=True)
t0 = time.time()
B, rem = screen(s0, r, d, n)
elapsed = time.time() - t0
print(f"SCREEN r={r} j={j} d={d} remdeg={rem.degree()} seconds={elapsed:.3f}", flush=True)
