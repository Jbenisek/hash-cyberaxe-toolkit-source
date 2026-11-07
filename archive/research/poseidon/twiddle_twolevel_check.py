"""Exact algebraic check for the proposed two-level r=1 twiddle table.

This is a research-only arithmetic check; it does not modify or build a
package.  The shipped table is tw[j] = rho**j for 0 <= j < 2**14, with
32-byte field elements.  The proposed replacement stores
T_hi[h] = rho**(128*h) and T_lo[l] = rho**l and reconstructs tw[j] as
T_hi[j >> 7] * T_lo[j & 127].
"""

P = 0x40000000000000000000000000000000224698FC094CF91B992D30ED00000001
N = 1 << 14
BASE = 1 << 7
rho = pow(5, (P - 1) // (1 << 15), P)

tw = [1] * N
for j in range(1, N):
    tw[j] = (tw[j - 1] * rho) % P
hi = [pow(rho, BASE * h, P) for h in range(BASE)]
lo = [pow(rho, l, P) for l in range(BASE)]

bad = []
for j, want in enumerate(tw):
    got = (hi[j >> 7] * lo[j & 127]) % P
    if got != want:
        bad.append(j)

# The inverse butterfly addresses the same table domain (nh-index), so check
# the derived indices too, including both endpoints used by the C source.
inverse_bad = []
nh = N
for idx in range(1, nh // 2):
    j = nh // 2 - idx
    got = (hi[j >> 7] * lo[j & 127]) % P
    if got != tw[j]:
        inverse_bad.append(j)

assert rho != 1 and pow(rho, 1 << 15, P) == 1 and pow(rho, 1 << 14, P) != 1
assert not bad and not inverse_bad
print({
    "order_rho": 1 << 15,
    "forward_entries_checked": N,
    "inverse_entries_checked": len(range(1, nh // 2)),
    "bad_forward": len(bad),
    "bad_inverse": len(inverse_bad),
    "full_bytes": N * 32,
    "two_level_bytes": (2 * BASE) * 32,
    "saved_bytes": (N - 2 * BASE) * 32,
})
