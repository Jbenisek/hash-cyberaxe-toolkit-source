"""Q4 (theta, first round): kernel of the column-parity map on the message space; weight-2 kernel vectors; do they all come from CP pairs."""
import json, itertools
from sha3lab import *
out = {}
for fmt, nv in (('F64', 512), ('F135', 1080)):
    cols = {}
    for k in range(nv):
        lane, z = divmod(k, 64); cols.setdefault((lane % 5, z), []).append(k)
    # parity map: each var -> its column; rank = number of occupied columns (each var hits exactly one column)
    rank = len(cols)
    w2 = sum(len(v) * (len(v) - 1) // 2 for v in cols.values())
    # explicit check: weight-2 vectors in kernel via brute force over pairs sharing a column == pairs; any weight-2 kernel vector must share a column
    # kernel is spanned by within-column pairs (each column's even-weight subspace)
    span_dim = sum(len(v) - 1 for v in cols.values())
    # verify theta is identity on kernel vectors: theta(state(d)^state(0)) == state(d)^state(0) for sample pairs
    import random
    rng = random.Random(3); okc = 0
    pairs = [(a, b) for v in cols.values() for a, b in itertools.combinations(v, 2)]
    for a, b in rng.sample(pairs, min(200, len(pairs))):
        d = (1 << a) | (1 << b); lanes = [(d >> (64*l)) & M64 for l in range(25)]
        okc += (theta(lanes) == lanes)
    out[fmt] = dict(nvars=nv, colparity_rank=rank, kernel_dim=nv - rank, pair_span_dim=span_dim, weight2_kernel_vectors=w2, theta_identity_on_200_pairs=okc,
                    columns_with_single_bit=sum(1 for v in cols.values() if len(v) == 1))
print(json.dumps(out, indent=1)); json.dump(out, open('q4_theta_out.json', 'w'), indent=1)
