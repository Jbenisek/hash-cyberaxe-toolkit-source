'''SAT timing of the 21-equation cyclic loop (the one remaining lever named in RESULT.md): encode the straight-line loop of
../solve.cu exactly (ripple-carry adders, XOR, rotations) for real instances of ../inst_2.txt, solve for g with kissat,
and compare with the GPU roots in ../roots_2.txt.  usage: python loopsat.py <n_instances> <time_cap_s> <seed>'''
import re, sys, random, subprocess, time, os
SRC = open('../solve.cu').read()
body = SRC[SRC.index('uint32_t g ='):SRC.index('int main')]
lines = re.findall(r'uint32_t (v_\w+) = (.*);', body)
chk = re.search(r'if \(\((.*)\) == 0u\)', body).group(1)
class CNF:
    def __init__(s): s.n = 1; s.cl = [[1]]          # var 1 = TRUE
    def var(s): s.n += 1; return s.n
    def xor2(s, a, b):
        if abs(a) == 1: return -b if a == 1 else b
        if abs(b) == 1: return -a if b == 1 else a
        c = s.var(); s.cl += [[-a, -b, -c], [a, b, -c], [a, -b, c], [-a, b, c]]; return c
    def maj(s, a, b, c):
        m = s.var(); s.cl += [[-a, -b, m], [-a, -c, m], [-b, -c, m], [a, b, -m], [a, c, -m], [b, c, -m]]; return m
F = CNF()
class W:
    def __init__(s, bits): s.b = bits                  # bits[i] = literal of bit i (1 = true, -1 = false)
    @staticmethod
    def const(x): return W([1 if x >> i & 1 else -1 for i in range(32)])
    def __xor__(s, o):
        o = o if isinstance(o, W) else W.const(o); return W([F.xor2(a, b) for a, b in zip(s.b, o.b)])
    __rxor__ = __xor__
    def add(s, o, cin=-1):
        o = o if isinstance(o, W) else W.const(o); out = []; c = cin
        for a, b in zip(s.b, o.b):
            out.append(F.xor2(F.xor2(a, b), c)); c = F.maj(a, b, c) if not (abs(a) == 1 and abs(b) == 1 and abs(c) == 1) else (1 if [a, b, c].count(1) >= 2 else -1)
        return W(out)
    def __add__(s, o): return s.add(o)
    def __radd__(s, o): return s.add(o)
    def __neg__(s): return W([-x for x in s.b]).add(W.const(0), cin=1)
    def __sub__(s, o):
        o = o if isinstance(o, W) else W.const(o); return s.add(W([-x for x in o.b]), cin=1)
    def __rsub__(s, o): return W.const(o) - s
def ROL(x, n): return W([x.b[(i - n) % 32] for i in range(32)])
def conv(e): return re.sub(r'0x([0-9a-f]+)u', r'0x\1', e)
inst = {}
for line in open('../inst_2.txt'):
    p = line.split(); inst[int(p[0])] = [int(x, 16) for x in p[1:]]
roots = {}
for line in open('../roots_2.txt'):
    p = line.split(); roots[int(p[0])] = [int(x, 16) for x in p[2:]]
n, cap, seed = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
rnd = random.Random(seed); ids = rnd.sample(sorted(k for k in roots if roots[k] or len(sys.argv) <= 4), n)
for pid in ids:
    global_F = CNF(); F.__dict__.update(global_F.__dict__)
    g = W([F.var() for _ in range(32)]); gv = list(g.b)
    env = {'g': g, 'ROL': ROL, 'P': [W.const(x) for x in inst[pid]]}
    for name, ex in lines: env[name] = eval(conv(ex), env)
    c = eval(conv(chk), env)
    if isinstance(c, int): c = W.const(c)
    for lit in c.b: F.cl.append([-lit])
    if len(sys.argv) > 4 and roots[pid]:          # control: pin g to a GPU root (expect SAT) or to root^1 (expect UNSAT)
        gfix = roots[pid][0] ^ (1 if sys.argv[4] == 'wrong' else 0)
        for i, v in enumerate(gv): F.cl.append([v if gfix >> i & 1 else -v])
    fn = 'loop_%d.cnf' % pid
    with open(fn, 'w', newline='\n') as f:
        f.write('p cnf %d %d\n' % (F.n, len(F.cl)))
        for cl in F.cl: f.write(' '.join(map(str, cl)) + ' 0\n')
    here = os.path.abspath('.').replace('\\', '/'); wsl = '/mnt/' + here[0].lower() + here[2:]
    t0 = time.time()
    out = subprocess.run(['wsl', '-e', 'bash', '-c', 'cd "%s" && /usr/bin/time -f "%%e" kissat --time=%d -q %s' % (wsl, cap, fn)],
                         capture_output=True, text=True)
    el = out.stderr.strip().splitlines()[-1] if out.stderr.strip() else '?'
    st = 'SAT' if '\ns SATISFIABLE' in '\n' + out.stdout else ('UNSAT' if 'UNSATISFIABLE' in out.stdout else 'UNKNOWN(cap)')
    gval = None
    if st == 'SAT':
        model = set()
        for line in out.stdout.splitlines():
            if line.startswith('v '): model |= {int(x) for x in line[2:].split()}
        gval = sum(1 << i for i, v in enumerate(gv) if v in model)
    print('instance %5d: GPU roots %d, kissat %s in %s s (cnf %d vars, %d clauses)%s' %
          (pid, len(roots[pid]), st, el, F.n, len(F.cl), '' if gval is None else ', g=%08x %s' % (gval, 'is a GPU root' if gval in roots[pid] else 'NOT a GPU root')))
    sys.stdout.flush(); os.remove(fn)
