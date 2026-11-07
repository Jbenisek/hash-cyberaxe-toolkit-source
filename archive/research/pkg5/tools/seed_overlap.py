#!/usr/bin/env python3
"""Do the per-thread random streams of r2_cls_gpu.cu (the class sampler) overlap inside one pair?

Thread state: s0 = L * 0x100000001B3 + tid * C, L = seed * 1000003 + index * 4099 + launch, and every
draw adds G = 0x9E3779B97F4A7C15 (splitmix64). Two threads replay each other if their s0 differ by j * G
with |j| below the number of draws of a thread (2 per iteration, at most 2^20 iterations).
Read-only arithmetic; nothing is run on the GPU.
"""
M = (1 << 64) - 1
C, G, F = 0xD6E8FEB86659FD93, 0x9E3779B97F4A7C15, 0x100000001B3
GINV = pow(G, -1, 1 << 64)
DRAWS = 1 << 21
hits = 0
closest = 1 << 64
for dl in range(0, 8):                       # launches of one pair (2^41 samples: 8 launches)
    base = dl * F
    for dt in range(-(1 << 18) + 1, 1 << 18):
        if dl == 0 and dt == 0:
            continue
        j = ((base + dt * C) * GINV) & M
        j = min(j, (1 << 64) - j)
        closest = min(closest, j)
        if j < DRAWS:
            hits += 1
print(f"thread pairs of one (eta, beta) pair that would share draws: {hits}")
print(f"closest stream distance: 2^{closest.bit_length() - 1} draws (a thread makes at most 2^21)")
