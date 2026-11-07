"""Our own Orchard PoseidonHash<ConstantLength<2>> (P128Pow5T3, Pallas base field) with a round-prefix parameter.

t=3, rate 2, capacity 1, S-box x^5, R_F=8 (rounds 0-3, 60-63), R_P=56 (rounds 4-59), 64 rounds.
Round i: state += RC[i]; S-box (all 3 lanes if full, lane 0 if partial); state = MDS * state.
Hash: init [m0, m1, 2^65], one permutation, digest = state[0]. No feed-forward.
Constants come from constants_own.py, generated from the PUBLIC halo2_poseidon-0.2.0 fp.rs (gen_constants.py).
Written independently; the PR 923 program was used only as DATA for cross-checking (see check_pr_constants.py).

Op counting (cost rule: one modular add or mult incl. squaring = 1 primitive):
  sbox  = 2 squarings (x^2, x^4) + 1 mult (x^5)        -> 3 mults (2 of them squarings)
  ARK   = 1 add per lane
  MDS   = 3 mults + 2 adds per output lane
Counter keeps add, sqr, mul separately (mul = non-squaring mults); mults_total = sqr + mul.
"""
from constants_own import P, ROUND_CONSTANTS, MDS, MDS_INV

WIDTH = 3
FULL_ROUNDS = 8
PARTIAL_ROUNDS = 56
TOTAL_ROUNDS = 64
CAPACITY = 2 << 64  # L * 2^64, L = 2  (= 2^65)


class Counter:
    """Exact primitive counter. add: modular additions; sqr: squarings; mul: other multiplications."""
    def __init__(self):
        self.add = 0; self.sqr = 0; self.mul = 0
    @property
    def mults(self): return self.sqr + self.mul
    @property
    def total(self): return self.add + self.sqr + self.mul          # additions + mults  (C = 27/round full)
    def copy(self):
        c = Counter(); c.add, c.sqr, c.mul = self.add, self.sqr, self.mul; return c
    def __sub__(self, o):
        c = Counter(); c.add = self.add - o.add; c.sqr = self.sqr - o.sqr; c.mul = self.mul - o.mul; return c
    def __repr__(self):
        return f"adds={self.add} sqr={self.sqr} mul={self.mul} | mults={self.mults} total={self.total}"


def is_full_round(i):
    return i < FULL_ROUNDS // 2 or i >= FULL_ROUNDS // 2 + PARTIAL_ROUNDS


def _add(a, b, c):
    if c: c.add += 1
    return (a + b) % P

def _mul(a, b, c):
    if c: c.mul += 1
    return a * b % P

def _sbox(x, c):
    if c: c.sqr += 2; c.mul += 1
    x2 = x * x % P
    x4 = x2 * x2 % P
    return x4 * x % P


def mds_mul(s, c=None, rows=(0, 1, 2)):
    out = []
    for i in range(3):
        if i not in rows:
            out.append(None); continue
        row = MDS[i]
        t = _mul(row[0], s[0], c)
        t = _add(t, _mul(row[1], s[1], c), c)
        t = _add(t, _mul(row[2], s[2], c), c)
        out.append(t)
    return out


def round_fn(s, i, c=None, rows=(0, 1, 2)):
    """One deployed round i (0-based). `rows` limits which MDS output lanes are computed (None for the rest)."""
    rc = ROUND_CONSTANTS[i]
    s = [_add(s[k], rc[k], c) for k in range(3)]
    if is_full_round(i):
        s = [_sbox(x, c) for x in s]
    else:
        s[0] = _sbox(s[0], c)
    return mds_mul(s, c, rows)


def perm(state, rounds=TOTAL_ROUNDS, counter=None, digest_only=False):
    """First `rounds` rounds of the deployed permutation (rounds in 0..64; 0 = identity).
    digest_only=True computes only MDS row 0 in the LAST executed round (other lanes returned as None)."""
    assert 0 <= rounds <= TOTAL_ROUNDS and len(state) == 3
    assert all(isinstance(x, int) and 0 <= x < P for x in state)
    s = list(state)
    for i in range(rounds):
        rows = (0,) if (digest_only and i == rounds - 1) else (0, 1, 2)
        s = round_fn(s, i, counter, rows)
    return s


def hash_prefix(m0, m1, r=TOTAL_ROUNDS, counter=None, digest_only=False):
    """Digest (field element) of the Orchard ConstantLength<2> hash truncated to the first r rounds."""
    assert r >= 1
    return perm([m0, m1, CAPACITY], r, counter, digest_only)[0]


def hash_prefix_bytes(data, r=TOTAL_ROUNDS):
    assert len(data) == 64
    m0 = int.from_bytes(data[:32], 'little'); m1 = int.from_bytes(data[32:], 'little')
    assert m0 < P and m1 < P, 'non-canonical'
    return hash_prefix(m0, m1, r).to_bytes(32, 'little')


# ---------------------------------------------------------------- optimized (still exact) evaluation
def hash_prefix_opt(m0, m1, r, counter=None, pre=None):
    """Same digest, fewer executed primitives, for fixed programs that hard-code derived constants:
      (a) lane 2 of round 0 is the constant K=2^65+RC[0][2]: its S-box and MDS column are precomputed constants,
          and the per-row constant M[i][2]*K^5 is folded into the next round's constants (or, for r==1, added once);
      (b) the last executed round computes only MDS row 0.
    `pre` (Counter) receives the one-time cost of deriving those constants (K, K^5, 3 products, 3 folds)."""
    assert r >= 1
    c = counter
    rc0 = ROUND_CONSTANTS[0]
    # one-time precompute
    K = _add(CAPACITY, rc0[2], pre)
    K5 = _sbox(K, pre)
    Ci = [_mul(MDS[i][2], K5, pre) for i in range(3)]
    a = _sbox(_add(m0, rc0[0], c), c)
    b = _sbox(_add(m1, rc0[1], c), c)
    if r == 1:
        t = _mul(MDS[0][0], a, c)
        t = _add(t, _mul(MDS[0][1], b, c), c)
        return _add(t, Ci[0], c)      # (the add of the constant Ci[0] is the one thing dropped by a comparison-only check)
    s = []
    for i in range(3):
        t = _mul(MDS[i][0], a, c)
        s.append(_add(t, _mul(MDS[i][1], b, c), c))   # constant Ci[i] folded into next ARK constant below
    for i in range(1, r):
        rc = list(ROUND_CONSTANTS[i])
        if i == 1:
            rc = [_add(rc[k], Ci[k], pre) for k in range(3)]   # one-time fold
        s = [_add(s[k], rc[k], c) for k in range(3)]
        s = [_sbox(x, c) for x in s] if is_full_round(i) else [_sbox(s[0], c), s[1], s[2]]
        s = mds_mul(s, c, (0,) if i == r - 1 else (0, 1, 2))
    return s[0]


def expected_counts(r, digest_only=False):
    """Analytic counts for perm(.., r) from the structure (adds, sqr, mul)."""
    add = sqr = mul = 0
    for i in range(r):
        lanes = 3 if is_full_round(i) else 1
        rows = 1 if (digest_only and i == r - 1) else 3
        add += 3 + rows * 2
        sqr += 2 * lanes
        mul += lanes + 3 * rows
    return add, sqr, mul
