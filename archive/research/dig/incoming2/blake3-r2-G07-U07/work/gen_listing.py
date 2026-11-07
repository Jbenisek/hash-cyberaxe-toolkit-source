import hashlib
T, F = 'T', 'F'
neg = lambda a: F if a == T else T if a == F else -a
class CNF:
 def __init__(s): s.n, s.cl, s.h = 0, [], {}
 def new(s, k=1): s.n += k; return list(range(s.n - k + 1, s.n + 1))
 def gate(s, k, f):
  o = s.h.get(k)
  if o is None: o = s.h[k] = s.new()[0]; s.cl += f(o)
  return o
 def x2(s, a, b):
  if a == F: return b
  if b == F: return a
  if a == T: return neg(b)
  if b == T: return neg(a)
  if a == b: return F
  if a == -b: return T
  p, q = sorted((abs(a), abs(b)))
  o = s.gate(('x', p, q), lambda o: [(-p, -q, -o), (p, q, -o), (p, -q, o), (-p, q, o)])
  return -o if (a < 0) ^ (b < 0) else o
 def a2(s, a, b):
  if a == F or b == F: return F
  if a == T: return b
  if b == T: return a
  if a == b: return a
  if a == -b: return F
  return s.gate(('a',) + tuple(sorted((a, b))), lambda o: [(-a, -b, o), (a, -o), (b, -o)])
 def or2(s, a, b): return neg(s.a2(neg(a), neg(b)))
 def x3(s, a, b, c):
  if T in (a, b, c) or F in (a, b, c) or len({abs(a), abs(b), abs(c)}) < 3: return s.x2(s.x2(a, b), c)
  k = ('x3',) + tuple(sorted((abs(a), abs(b), abs(c))))
  def f(o):
   p, q, r = k[1:]
   return [tuple(-l for l in (p if m & 1 else -p, q if m & 2 else -q, r if m & 4 else -r)) + (o if bin(m).count('1') & 1 else -o,) for m in range(8)]
  o = s.gate(k, f)
  return -o if (a < 0) ^ (b < 0) ^ (c < 0) else o
 def maj(s, a, b, c):
  for x, y, z in ((a, b, c), (b, c, a), (c, a, b)):
   if x == F: return s.a2(y, z)
   if x == T: return s.or2(y, z)
  if a == b or a == c: return a
  if b == c: return b
  if a == -b: return c
  if a == -c: return b
  if b == -c: return a
  return s.gate(('m',) + tuple(sorted((a, b, c))), lambda o: [(-a, -b, o), (-a, -c, o), (-b, -c, o), (a, b, -o), (a, c, -o), (b, c, -o)])
 def add(s, x, y):
  out, cy = [], F
  for i in range(len(x)):
   out.append(s.x3(x[i], y[i], cy))
   if i < len(x) - 1: cy = s.maj(x[i], y[i], cy)
  return out
 def xor(s, x, y): return [s.x2(p, q) for p, q in zip(x, y)]
 def eq(s, a, b):
  d = s.x2(a, b)
  if d == T: s.cl.append(())
  elif d != F: s.cl.append((-d,))
 def eqw(s, x, y):
  for p, q in zip(x, y): s.eq(p, q)
 def atmost(s, ls, b):
  ls = [l for l in ls if l != F]
  b -= ls.count(T)
  ls = [l for l in ls if l != T]
  if b < 0: s.cl.append(()); return
  if b >= len(ls): return
  if b == 0: s.cl += [(-l,) for l in ls]; return
  pv = None
  for x in ls:
   cu = s.new(b)
   s.cl.append((-x, cu[0]))
   if pv:
    s.cl += [(-pv[j], cu[j]) for j in range(b)]
    s.cl += [(-x, -pv[j - 1], cu[j]) for j in range(1, b)]
    s.cl.append((-x, -pv[b - 1]))
   pv = cu
 def dimacs(s): return (f"p cnf {s.n} {len(s.cl)}\n" + "".join(" ".join(map(str, c)) + " 0\n" for c in s.cl)).encode()
const = lambda v, w: [T if (v >> i) & 1 else F for i in range(w)]
ror = lambda x, r: x[r:] + x[:r]
def G(s, v, x, y, R):
 a, b, c, d = v
 a = s.add(s.add(a, b), x); d = ror(s.xor(d, a), R[0]); c = s.add(c, d); b = ror(s.xor(b, c), R[1])
 a = s.add(s.add(a, b), y); d = ror(s.xor(d, a), R[2]); c = s.add(c, d); b = ror(s.xor(b, c), R[3])
 return [a, b, c, d]
def gen(w, R, K, lx, top0, bound, maxx1):
 s = CNF()
 nw = lambda: s.new(w)
 X = [nw() for _ in range(4)]
 w4, w13 = nw(), nw()
 w13 = w13[:w - top0] + [F] * top0
 w4b = nw()
 s.eqw(s.add(const(K, w), w4b), s.xor(s.add(const(K, w), w4), const(lx, w)))
 va, vb = G(s, X, w4, w13, R), G(s, X, w4b, w13, R)
 s.eqw(va[1], vb[1]); s.eqw(va[3], vb[3])
 y3, y3b, y11, y11b = va[0], vb[0], va[2], vb[2]
 dw = nw()
 s.eqw(s.add(dw, w4b), w4)
 a1, y12, y6, w5 = nw(), nw(), nw(), nw()
 d1 = ror(s.xor(y12, a1), R[0])
 e1o = []
 for ci, m2 in ((y11, w5), (y11b, s.add(w5, dw))):
  c1 = s.add(ci, d1); b1 = ror(s.xor(y6, c1), R[1]); a2 = s.add(s.add(a1, b1), m2)
  d2 = ror(s.xor(d1, a2), R[2]); c2 = s.add(c1, d2); b2 = ror(s.xor(b1, c2), R[3])
  e1o.append((c1, b1, a2, d2, c2, b2))
 y4, y9, y14, w8 = nw(), nw(), nw(), nw()
 e3o = []
 for ai in (y3, y3b):
  e1 = s.add(ai, y4); h1 = ror(s.xor(y14, e1), R[0]); g1 = s.add(y9, h1); f1 = ror(s.xor(y4, g1), R[1])
  e2 = s.add(s.add(e1, f1), w8); h2 = ror(s.xor(h1, e2), R[2]); g2 = s.add(g1, h2); f2 = ror(s.xor(f1, g2), R[3])
  e3o.append((e1, h1, g1, f1, e2, h2, g2, f2))
 x5, beta, tau, nu, eps, db2 = [s.xor(p, q) for p, q in zip(*e1o)]
 x1, eta, x2, psi, de2, mu, dg2, df2 = [s.xor(p, q) for p, q in zip(*e3o)]
 s.eqw(tau, dg2); s.eqw(de2, eps); s.eqw(df2, nu); s.eqw(db2, mu)
 for i in range(w):
  j = (i + 1) % w
  s.eq(psi[i], s.x2(tau[i], tau[j]))
  s.eq(s.x2(beta[i], eps[i]), s.x2(eta[j], eps[j]))
 orw = lambda p, q: [s.or2(p[i], q[i]) for i in range(w)]
 parts = [x5, orw(beta, tau), orw(nu, eps), orw(eta, x2), orw(psi, eps), orw(mu, tau)]
 s.atmost([b for p in parts for b in p[:w - 1]], bound)
 if maxx1 >= 0: s.atmost(x1[:w - 1], maxx1)
 d3 = nw(); s.eqw(s.add(d3, y3), y3b)
 d11 = nw(); s.eqw(s.add(d11, y11), y11b)
 return s, dict(X3=X[0], X7=X[1], X11=X[2], X15=X[3], W4=w4, W13=w13, d1=d1, b1=e1o[0][1], a2=e1o[0][2],
  Y4=y4, h1=e3o[0][1], Y9=y9, w8=w8)
def value(model, word):
 return sum(1 << i for i, b in enumerate(word) if b == T or (b != F and model[abs(b)] == (b > 0)))
def check(w, R, K, lx, top0, bound, maxx1, pin, sol):
 M = (1 << w) - 1
 rr = lambda x, r: ((x >> r) | (x << (w - r))) & M
 rl = lambda x, r: rr(x, w - r)
 X3, X7, X11, X15, W4, W13 = pin
 d1, b1, a2, Y4, h1, Y9, w8 = sol
 W4b = (((K + W4) & M) ^ lx) - K & M
 def g(a, b, c, d, x, y):
  a = (a + b + x) & M; d = rr(d ^ a, R[0]); c = (c + d) & M; b = rr(b ^ c, R[1])
  a = (a + b + y) & M; d = rr(d ^ a, R[2]); c = (c + d) & M; b = rr(b ^ c, R[3])
  return a, b, c, d
 A, B = g(X3, X7, X11, X15, W4, W13), g(X3, X7, X11, X15, W4b, W13)
 ok = A[1] == B[1] and A[3] == B[3] and W13 >> (w - top0) == 0
 dw = (W4 - W4b) & M
 c1 = (A[2] + d1) & M
 y6 = rl(b1, R[1]) ^ c1
 s1 = (a2 - b1) & M
 e1 = []
 for Y11, m in ((A[2], 0), (B[2], dw)):
  c1 = (Y11 + d1) & M; b1x = rr(y6 ^ c1, R[1]); a2x = (s1 + b1x + m) & M
  d2 = rr(d1 ^ a2x, R[2]); c2 = (c1 + d2) & M; b2 = rr(b1x ^ c2, R[3])
  e1.append((c1, b1x, a2x, d2, c2, b2))
 y14 = rl(h1, R[0]) ^ ((A[0] + Y4) & M)
 e3 = []
 for Y3 in (A[0], B[0]):
  ee1 = (Y3 + Y4) & M; hh1 = rr(y14 ^ ee1, R[0]); g1 = (Y9 + hh1) & M; f1 = rr(Y4 ^ g1, R[1])
  e2 = (ee1 + f1 + w8) & M; h2 = rr(hh1 ^ e2, R[2]); g2 = (g1 + h2) & M; f2 = rr(f1 ^ g2, R[3])
  e3.append((ee1, hh1, g1, f1, e2, h2, g2, f2))
 x5, beta, tau, nu, eps, db2 = [p ^ q for p, q in zip(*e1)]
 x1, eta, x2, psi, de2, mu, dg2, df2 = [p ^ q for p, q in zip(*e3)]
 ok = ok and tau == dg2 and de2 == eps and df2 == nu and db2 == mu
 low = M >> 1
 cost = sum(bin(v & low).count('1') for v in (x5, beta | tau, nu | eps, eta | x2, psi | eps, mu | tau))
 x1w = bin(x1 & low).count('1')
 return ok and cost <= bound and (maxx1 < 0 or x1w <= maxx1), cost, x1w, eta, beta
s, words = gen(32, (16, 12, 8, 7), 0x5bf2cd1d, 8, 8, 104, 24)
data = s.dimacs()
assert hashlib.sha256(data).hexdigest() == "286927dd9581cc54055b1db8ca6039d76c712041e14c0cf4cdb285d6bd743ee8"
open("run20.cnf", "wb").write(data)
pin = (0x29d4fa98, 0xbee3af28, 0x44036000, 0x40c58500, 0x97475638, 0x0007c006)
sol = (0x27e956dc, 0x027077ff, 0x800817b3, 0xe614819a, 0x615469a6, 0x9ff1dcb4, 0x6fc881ad)
ok, cost, x1w, eta, beta = check(32, (16, 12, 8, 7), 0x5bf2cd1d, 8, 8, 104, 24, pin, sol)
print(ok, cost, x1w, "%08x %08x" % (eta, beta))
