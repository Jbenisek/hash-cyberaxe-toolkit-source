"""Small, owned reconnaissance for BLAKE3 schedule-invariant differences.

This is deliberately not a package builder or a contest submission program.  It
records round states for a scalar pair and checks whether a difference repeat is
also accompanied by pair-state and carry-signature repeats.  The latter two
checks prevent a Hamming-similarity spike from being mistaken for a closed
differential recurrence.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[1] / "catalogue" / "verify_5"))
import b3own  # own reference implementation used by the existing catalogue checks


MASK = 0xFFFFFFFF
CYCLE0 = frozenset((0, 2, 3, 5, 9, 10, 11, 12))
CYCLE1 = frozenset((1, 4, 6, 7, 8, 13, 14, 15))


def round_step(state, words):
    """One BLAKE3 round, returning state and four carry masks per G."""
    v = list(state)
    carries = []
    for i, (a, bb, c, d) in enumerate(b3own.CALLS):
        x, y = words[2 * i], words[2 * i + 1]
        carry_a, aa = divmod(v[a] + v[bb] + x, 1 << 32)
        dd = b3own.ror(v[d] ^ aa, 16)
        carry_c, cc = divmod(v[c] + dd, 1 << 32)
        b1 = b3own.ror(v[bb] ^ cc, 12)
        carry_a2, a2 = divmod(aa + b1 + y, 1 << 32)
        d2 = b3own.ror(dd ^ a2, 8)
        carry_c2, c2 = divmod(cc + d2, 1 << 32)
        b2 = b3own.ror(b1 ^ c2, 7)
        v[a], v[bb], v[c], v[d] = a2, b2, c2, d2
        carries.append((carry_a, carry_c, carry_a2, carry_c2))
    return tuple(v), tuple(carries)


def start_state():
    return tuple(b3own.IV + b3own.IV[:4] + (0, 0, 64, 11))


def trajectory(words, rounds=32):
    state = start_state()
    scheduled = tuple(words)
    states, carries = [], []
    for _ in range(rounds):
        state, carry = round_step(state, scheduled)
        states.append(state)
        carries.append(carry)
        scheduled = tuple(scheduled[p] for p in b3own.PERM)
    return states, carries


def invariant_delta(u, v):
    return tuple(u if i in CYCLE0 else v for i in range(16))


def hamming_similarity(x, y):
    bits = sum((a ^ b).bit_count() for a, b in zip(x, y))
    return 1.0 - bits / (32 * len(x))


def centered_similarity(x, y):
    return 1.0 - 2.0 * sum((a ^ b).bit_count() for a, b in zip(x, y)) / (32 * len(x))


def carry_equal(x, y):
    return x == y


def report_pair(words_a, words_b, rounds=32):
    a_states, a_carries = trajectory(words_a, rounds)
    b_states, b_carries = trajectory(words_b, rounds)
    diffs = [tuple(a ^ b for a, b in zip(x, y)) for x, y in zip(a_states, b_states)]
    pair_states = list(zip(a_states, b_states))
    pair_carries = list(zip(a_carries, b_carries))
    rows = []
    for lag in (1, 2, 4, 8, 16):
        if lag >= rounds:
            continue
        sims = [centered_similarity(diffs[r], diffs[r + lag]) for r in range(rounds - lag)]
        exact_d = sum(diffs[r] == diffs[r + lag] for r in range(rounds - lag))
        exact_pair = sum(pair_states[r] == pair_states[r + lag] for r in range(rounds - lag))
        exact_carry = sum(carry_equal(pair_carries[r], pair_carries[r + lag]) for r in range(rounds - lag))
        rows.append({
            "lag": lag,
            "diff_centered_max": round(max(sims), 6),
            "diff_centered_mean": round(sum(sims) / len(sims), 6),
            "diff_exact": f"{exact_d}/{rounds-lag}",
            "pair_exact": f"{exact_pair}/{rounds-lag}",
            "carry_exact": f"{exact_carry}/{rounds-lag}",
        })
    return rows


def reference_check(words):
    """Cross-check the first two owned rounds against b3own.compress_full."""
    ours, _ = trajectory(words, 2)
    _, states = b3own.compress_full(tuple(b3own.IV), tuple(words), 0, 64, 11, rounds=2)
    return ours[0] == tuple(states["X"]) and ours[1] == tuple(states["Z"])


def main():
    rng = random.Random(20261019)
    print("permutation_cycles", [
        [0, 2, 3, 10, 12, 9, 11, 5],
        [1, 6, 4, 7, 13, 14, 15, 8],
    ])
    kat_words = [rng.getrandbits(32) for _ in range(16)]
    print("owned_reference_check", reference_check(kat_words))
    for kind in ("delta_only", "both_invariant", "control"):
        print("case", kind)
        aggregate = {lag: [] for lag in (1, 2, 4, 8, 16)}
        exact_totals = {key: 0 for key in ("diff_exact", "pair_exact", "carry_exact")}
        for trial in range(8):
            u = rng.getrandbits(32) or 1
            v = rng.getrandbits(32) or 1
            delta = invariant_delta(u, v)
            base = [rng.getrandbits(32) for _ in range(16)]
            if kind == "both_invariant":
                base = list(invariant_delta(rng.getrandbits(32), rng.getrandbits(32)))
            elif kind == "control":
                delta = tuple(rng.getrandbits(32) for _ in range(16))
            other = [x ^ d for x, d in zip(base, delta)]
            rows = report_pair(base, other)
            print(trial, rows)
            for row in rows:
                aggregate[row["lag"]].append(row["diff_centered_max"])
                for key in exact_totals:
                    exact_totals[key] += int(row[key].split("/")[0])
        print("summary", kind, {
            "max_centered_by_lag": {lag: max(vals) for lag, vals in aggregate.items()},
            "max_centered_any": max(max(vals) for vals in aggregate.values()),
            "exact_repeat_numerators": exact_totals,
        })


if __name__ == "__main__":
    main()
