"""D352: one preregistered Poseidon r2 d=78125 decomposition screen."""
from decomp import *
import time

r = 2
j = 0
d = 78125
n = 5 ** (6 + r)
L = Line(j)
s0 = s0_line(L)
print(f"START r={r} j={j} d={d} n={n}", flush=True)
t0 = time.time()
B, rem = screen(s0, r, d, n)
elapsed = time.time() - t0
print(f"SCREEN r={r} j={j} d={d} n={n} remdeg={rem.degree()} seconds={elapsed:.3f}", flush=True)
