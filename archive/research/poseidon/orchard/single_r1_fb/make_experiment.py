"""Build the package parts that depend on found collisions: experiments/replay.py (+ manifest) and certificates.
For every verified collision the root S = ((W1-W2)/2)^2 of the odd-part polynomial is recovered from (nk,rho) pairs through the
line model, so the replay program needs only (j, centre c, S)."""
import json, os, sys, hashlib
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'pkg_stage')
NCERT = int(sys.argv[2]) if len(sys.argv) > 2 else 3
NOEXP = len(sys.argv) > 3 and sys.argv[3] == 'noexp'
C = json.load(open(os.path.join(HERE, '..', '..', 'pareto_clone', 'pareto', 'orchard-pallas-constants.json')))
P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
MDS = [[int(x, 16) for x in r] for r in C['mds']]
RC0 = [int(x, 16) for x in C['round_constants'][0]]
RC1 = [int(x, 16) for x in C['round_constants'][1]]
CAP = 1 << 65
E5 = (4 * (P - 1) + 1) // 5
assert 5 * E5 % (P - 1) == 1

def solve2(a, b, c, d, e, f):
    inv = pow((a * d - b * c) % P, -1, P)
    return ((e * d - b * f) * inv) % P, ((a * f - e * c) * inv) % P
def line(j):
    K = pow((CAP + RC0[2]) % P, 5, P)
    I = [k for k in range(3) if k != j]
    base = [(MDS[k][2] * K + RC1[k]) % P for k in range(3)]
    i1, i2 = I
    UQ, VQ = solve2(MDS[i1][0], MDS[i1][1], MDS[i2][0], MDS[i2][1], -base[i1] % P, -base[i2] % P)
    return UQ, VQ, MDS[j][1], (-MDS[j][0]) % P
def inputs(j, W):
    UQ, VQ, a, b = line(j)
    tau = pow(W, E5, P)
    return (pow((UQ + tau * a) % P, E5, P) - RC0[0]) % P, (pow((VQ + tau * b) % P, E5, P) - RC0[1]) % P
def invert(j, nk, rho):
    UQ, VQ, a, b = line(j)
    U = pow((nk + RC0[0]) % P, 5, P)
    tau = ((U - UQ) * pow(a, -1, P)) % P
    return pow(tau, 5, P)

colls = json.load(open(os.path.join(HERE, 'data', 'collisions.json')))
triples = []
for v in colls:
    if not v['verified']: continue
    j = v['j']
    W1, W2 = invert(j, v['nk1'], v['rho1']), invert(j, v['nk2'], v['rho2'])
    h = pow(2, -1, P)
    c, s = (W1 + W2) * h % P, (W1 - W2) * h % P
    assert c == v['centre'], 'centre mismatch'
    S = s * s % P
    assert inputs(j, (c + s) % P) == (v['nk1'], v['rho1']) or inputs(j, (c + s) % P) == (v['nk2'], v['rho2'])
    triples.append((j, c, S))
triples = sorted(set(triples))
print('triples', len(triples))

SRC = '''"""Replay of attack outputs at the selected target (evidence, not a cost claim).
Each stored triple (j, c, S) is a centre c and a root S of the odd-part polynomial g_c found by the attack of proof.md.
The program re-derives, from the deployed round constants only, the line of proof.md section 2, the two line parameters
W = c +- sqrt(S), tau = W^e and the two canonical inputs (nk,rho); the host recomputes both digests."""
import json, sys
P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
CAP = 1 << 65
MDS = %(mds)s
RC0 = %(rc0)s
RC1 = %(rc1)s
E5 = (4 * (P - 1) + 1) // 5
TRIPLES = %(triples)s

def sqrt_mod(a):
    q, s = P - 1, 0
    while q %% 2 == 0: q //= 2; s += 1
    z = 5
    c, t, r, m = pow(z, q, P), pow(a, q, P), pow(a, (q + 1) // 2, P), s
    while t != 1:
        i, t2 = 0, t
        while t2 != 1: t2 = t2 * t2 %% P; i += 1
        b = pow(c, 1 << (m - i - 1), P)
        r, c = r * b %% P, b * b %% P
        t, m = t * c %% P, i
    return r

def line(j):
    K = pow((CAP + RC0[2]) %% P, 5, P)
    i1, i2 = [k for k in range(3) if k != j]
    base = [(MDS[k][2] * K + RC1[k]) %% P for k in range(3)]
    a, b, c, d = MDS[i1][0], MDS[i1][1], MDS[i2][0], MDS[i2][1]
    e, f = -base[i1] %% P, -base[i2] %% P
    inv = pow((a * d - b * c) %% P, -1, P)
    return ((e * d - b * f) * inv) %% P, ((a * f - e * c) * inv) %% P, MDS[j][1], (-MDS[j][0]) %% P

def inputs(ln, W):
    UQ, VQ, a, b = ln
    tau = pow(W, E5, P)
    return (pow((UQ + tau * a) %% P, E5, P) - RC0[0]) %% P, (pow((VQ + tau * b) %% P, E5, P) - RC0[1]) %% P

def message(nk, rho):
    return (nk.to_bytes(32, "little") + rho.to_bytes(32, "little")).hex()

def pair(j, c, S):
    ln = line(j)
    s = sqrt_mod(S)
    assert s * s %% P == S
    x1, x2 = inputs(ln, (c + s) %% P), inputs(ln, (c - s) %% P)
    return message(*x1), message(*x2)

def main():
    request = json.load(sys.stdin)
    cache = {}
    trials = []
    for item in request["trials"]:
        i = item["trial"] %% len(TRIPLES)
        if i not in cache: cache[i] = pair(*TRIPLES[i])
        a, b = cache[i]
        trials.append({"trial": item["trial"], "message_a_hex": a, "message_b_hex": b})
    sys.stdout.write(json.dumps({"schema_version": 1, "trials": trials}, separators=(",", ":")))

main()
'''
def fmt(t): return repr(tuple(tuple(hex(x) for x in r) if isinstance(r, (list, tuple)) else hex(r) for r in t)).replace("'", "'")
src = SRC % dict(mds=repr(tuple(tuple(r) for r in MDS)).replace('(', '(').replace(' ', ' '),
                 rc0=repr(tuple(RC0)), rc1=repr(tuple(RC1)),
                 triples='(\n' + ''.join('    (%d, %s, %s),\n' % (j, hex(c), hex(S)) for j, c, S in triples) + ')')
if not NOEXP:
    os.makedirs(os.path.join(OUT, 'experiments'), exist_ok=True)
    open(os.path.join(OUT, 'experiments', 'replay.py'), 'w', newline='\n').write(src)
    man = {"schema_version": 1, "experiments": [{
        "id": "replay-attack-outputs", "kind": "python-message-pairs-v1",
        "scope": "Selected target r=1; %d stored (line j, centre c, root S) triples produced by the attack of proof.md; each trial re-derives one colliding input pair from its triple (trials repeat the triples cyclically, so repeated pairs are expected)." % len(triples),
        "hypothesis": "For a root S of g_c, the inputs built by the back-map of proof.md section 5 are distinct canonical pairs with equal selected-target digests; no claim about cost, success rate or how the triples were found.",
        "program": "experiments/replay.py", "event": {"kind": "full-collision"}}]}
    json.dump(man, open(os.path.join(OUT, 'experiments', 'manifest.json'), 'w', newline='\n'), indent=1)
# certificates: up to NCERT verified collisions from different seeds, lines taken in turn
os.makedirs(os.path.join(OUT, 'certificates'), exist_ok=True)
ver = sorted((v for v in colls if v['verified']), key=lambda v: v['seed'])
chosen, byj = [], {0: [v for v in ver if v['j'] == 0], 1: [v for v in ver if v['j'] == 1], 2: [v for v in ver if v['j'] == 2]}
k = 0
while len(chosen) < min(NCERT, len(ver)):
    q = byj[k % 3]
    if q: chosen.append(q.pop(0))
    k += 1
    if k > 10 * len(ver) + 10: break
certs = []
for n, v in enumerate(chosen):
    ma = v['nk1'].to_bytes(32, 'little') + v['rho1'].to_bytes(32, 'little'); mb = v['nk2'].to_bytes(32, 'little') + v['rho2'].to_bytes(32, 'little')
    open(os.path.join(OUT, 'certificates', 'c%d-a.bin' % (n + 1)), 'wb').write(ma); open(os.path.join(OUT, 'certificates', 'c%d-b.bin' % (n + 1)), 'wb').write(mb)
    certs.append({"id": "collision-%d" % (n + 1), "type": "hash-collision-witness-v2", "message_a": "certificates/c%d-a.bin" % (n + 1),
                  "message_b": "certificates/c%d-b.bin" % (n + 1), "expected_digest": v['digest'].to_bytes(32, 'little').hex(), "target_profile": "poseidon-orchard-r1-prefix-v1"})
json.dump({"schema_version": 2, "certificates": certs}, open(os.path.join(OUT, 'certificates', 'manifest.json'), 'w', newline='\n'), indent=1)
print('certificates', len(certs), 'lines', sorted(set(v['j'] for v in chosen)), 'triples', len(triples))
