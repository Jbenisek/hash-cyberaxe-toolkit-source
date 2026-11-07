"""Bucket model of the wall time of one trial (SPEEDUP.md section 5), built from the r3 profiles (prof_out/r3_base1_T8_err.txt, r3_fast1_T8_err.txt).
Work per bucket is in thread-seconds of the local r3 profile (8 threads); each bucket runs at min(T, cap) threads with efficiency eff.
Scaling to r: C (stage C, fully parallel) by its operation count; every half-gcd level by m (each level costs about the same per unit of m), and the
levels above a = 18 (absent at r3) are added as fully parallel levels.  The local thread-second is converted to the cloud box with the factor that makes
the model reproduce the measured r5 run (21,946 s at T = 16, exec_r5mt).  usage: python3 estimate.py"""
import math
p = 0.39; q = 1 - p
# r3 profile buckets (thread-s): (work, cap, eff)
BASE = {
    'D base case + mat_mulQ + divrem (serial)': (81.8, 1, 1.0),
    'D levels a <= 10 (serial)':               (70.3, 1, 1.0),
    'D level a = 15 (serial in exec_r6mt)':     (56.0, 1, 1.0),
    'D levels a = 11..14 (3 rows)':             (155.9, 3, 0.87),
    'D level a = 16 (2 threads)':               (59.0, 2, 0.95),
    'D level a = 17 (4 threads)':               (64.3, 4, 0.83),
    'D level a = 18 (8 threads)':               (92.0, 8, 0.66),
}
FAST = {
    'D base case + mat_mulQ + divrem (serial)': (81.8, 1, 1.0),
    'D levels a <= 10 (serial)':               (58.2, 1, 1.0),
    'D levels a = 11..14 (task mode)':          (160.0, 10, 0.7),
    'D level a = 15 (sub-tree mode)':           (48.4, 4, 0.8),
    'D level a = 16 (sub-tree mode)':           (55.8, 8, 0.75),
    'D level a = 17 (sub-tree mode)':           (70.4, 16, 0.7),
    'D level a = 18 (sub-tree mode)':           (89.8, 32, 0.7),
}
C_R3 = 6075.0           # stage C thread-s at r3 (busy + serial, base profile)
C_EFF = 0.89            # measured: 7.15 busy threads per 8 in the stage C dispatches
D_LEVEL = 80.0          # thread-s of one half-gcd level at r3 scale (a = 16..18 measured 59-92)
OPS_C_R3 = 345.9e9      # stage C operations of one r3 trial (exec_r6mt lineage)
ROUNDS = {  # m ratio to r3, stage C ops per trial (rows3 / with the rows-2 chooser), number of half-gcd levels above a = 18
    5: dict(mr=25, C3=6.585e12, C2=6.585e12, top=4),
    6: dict(mr=125, C3=6.03e13, C2=4.02e13, top=8),
    7: dict(mr=625, C3=2.59e14, C2=2.59e14, top=10),
}
def wall(r, T, buckets, rows2):
    R = ROUNDS[r]; t = 0.0
    for name, (w, cap, eff) in buckets.items():
        t += w * R['mr'] / (min(T, cap) * (eff if min(T, cap) > 1 else 1.0))
    t += R['top'] * D_LEVEL * R['mr'] * (0.8 if rows2 else 1.0) / (T * C_EFF)
    C = (R['C2'] if rows2 else R['C3']) / OPS_C_R3 * C_R3
    t += C / (T * C_EFF)
    return t
cal = 21946.0 / wall(5, 16, BASE, False)
print(f'cloud factor (r5 measured 21,946 s at T=16 / model): {cal:.2f}')
for r in (6, 7):
    print(f'\n## r{r}: wall per trial (h, cloud scale), exec_r6mt vs exec_r6fast (rows 2 at r6 only where it fits)')
    print('| T | exec_r6mt | exec_r6fast | of which serial floor (fast) |')
    print('|---|---:|---:|---:|')
    for T in (24, 32, 64, 96):
        b = wall(r, T, BASE, False) * cal / 3600; f = wall(r, T, FAST, r == 6) * cal / 3600
        fl = sum(w * ROUNDS[r]['mr'] for n, (w, cap, e) in FAST.items() if cap == 1) * cal / 3600
        print(f'| {T} | {b:.1f} | {f:.1f} | {fl:.1f} |')
    print(f'\n## r{r}: speculative centres (exec_r6fast), expected wall to the first success (h); waves E = 1/(1-q^k), p = {p}')
    print('| threads in total | k | threads each | wall per trial (h) | E waves | expected wall (h) |')
    print('|---|---|---|---:|---:|---:|')
    for T in (24, 32, 64, 96):
        for k in (1, 2, 3):
            t = T // k; w = wall(r, t, FAST, r == 6) * cal / 3600; E = 1 / (1 - q ** k)
            print(f'| {T} | {k} | {t} | {w:.1f} | {E:.3f} | {w*E:.1f} |')
