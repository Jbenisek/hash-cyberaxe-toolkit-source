# cm4.py R KR100 KAPPA ENTRY KEYS PI : full stack on g/r{R}_k{KR}.py: prefix KEYS (8 hex words, comma), input polarity PI (hex; recovery +8 XORs),
# U3 7-B table when ENTRY = 7. KAT: step(S) == f(S ^ PI) ^ q on 256 random lanes.
import sys, os, importlib.util, json, random
from math import log2
sys.setrecursionlimit(100000); sys.dont_write_bytecode = True
R, KR, K, E = (int(a) for a in sys.argv[1:5]); KEYS = [int(h, 16) for h in sys.argv[5].split(",")]; PI = int(sys.argv[6], 16)
f = os.path.join(os.path.dirname(os.path.abspath(__file__)), "g", "r%d_k%d.py" % (R, KR))
spec = importlib.util.spec_from_file_location("bsm", f); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
m.KEY = KEYS; m.KEYINT = sum(k << (32 * i) for i, k in enumerate(KEYS))
oi = m.Gen.__init__
def init(self, n):
    oi(self, n); self.inputs = [(nd, (PI >> j) & 1) for j, (nd, _) in enumerate(self.inputs)]
m.Gen.__init__ = init
opc = m.packed_circuit
xtra = 8 if PI else 0
m.packed_circuit = lambda qw: (lambda r: (r[0], r[1] + xtra) + tuple(r[2:]))(opc(qw))
m._STEP256.clear()
st = m.step256()
rnd = random.Random(7); xs = [rnd.getrandbits(256) for _ in range(256)]
o = m.lanes_of(list(st.step(*m.pack_lanes(xs, 256, st.pin))), 256, st.pin)
kat = all(o[l] == m.f_scalar(xs[l] ^ PI, 256) ^ st.qint for l in range(256))
RG = 800
if E == 7:
    m.ENTRY, m.TBITS, m.KEYBITS = 7, 17, 7 * 8 - 17
    tmax = m.machine_constants(st, RG)[4]; l = tmax.bit_length() - 1
    m.KEYBITS = 56 - 17 - 3 + l; m.EVENT_OPS = m.EVENT_OPS + 4 * tmax
else:
    tmax = m.machine_constants(st, RG)[4]
lo, hi = 1.0, float(tmax + 1)
for _ in range(60):
    mid = (lo + hi) / 2
    lo, hi = (mid, hi) if m.tail_log2(mid, tmax + 1) <= m.TAIL_LOG2 else (lo, mid)
sb = m.CFG[256]["Sb"]
ok = lambda T: m._lossq(T, lo, tmax, K, sb)["P_lower"] >= m.P_MIN
a, b = 1000, 6000
while b - a > 1:
    mm = (a + b) // 2
    a, b = (mm, b) if ok(mm) else (a, mm)
m._B.clear(); p = m._plan(256, a, K, tmax, sb); lo2 = m.loss(p); lg = m.ledger(p, st, RG)
print(json.dumps(dict(R=R, kr=KR, kappa=K, entry=E, kat=kat, gates=st.ops, packed=m.packed_circuit(st.qwords)[1], tmax=tmax, Tp=a, P=lo2["P_lower"],
      rec_frac=float(lg["parts"]["recovery"] / lg["total"]), tl=log2(lg["total"] / m.UNIT))), flush=True)
