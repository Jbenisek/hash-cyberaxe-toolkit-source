# t_imm_d.py - sensitivity: the shipped online program and the preprocessing bodies of this derivative re-measured with every immediate operand of an
# ALU instruction, compare-branch or store charged one extra operation (as if loaded by an `li`; the class MI of the base's t_imm.py); then the ledger.
# usage: t_imm_d.py <dir of vt38.py> <dir of src/ (t_pre1.py, t_pre_d.py, ledger38.py)> <scratch runs dir>
import sys, os, json, io, contextlib
VT, SRC, RUNS = sys.argv[1:4]; sys.path.insert(0, VT); sys.path.insert(0, SRC); sys.dont_write_bytecode = True
import vt38
from vt38 import *
class MI(Machine):
    def run(s, code, maxops=None):
        c, lab, r = code.c, code.lab, s.r; pc = 0; n = len(c); mem = s.mem
        def v(x): return x if isinstance(x, int) else r.get(x, 0)
        ops = 0
        isi = lambda x: isinstance(x, int)
        while pc < n:
            ins = c[pc]; op = ins[0]; pc += 1
            if op in ('add', 'sub', 'and', 'or', 'xor'): ops += isi(ins[2]) + isi(ins[3])
            elif op == 'rsub': ops += 1 + isi(ins[3])
            elif op == 'bne': ops += isi(ins[2])
            elif op == 'sti': ops += isi(ins[2])
            if op == 'add': r[ins[1]] = (v(ins[2]) + v(ins[3])) & WORD; ops += 1
            elif op == 'sub': r[ins[1]] = (v(ins[2]) - v(ins[3])) & WORD; ops += 1
            elif op == 'rsub': r[ins[1]] = (ins[2] - v(ins[3])) & WORD; ops += 1
            elif op == 'and': r[ins[1]] = v(ins[2]) & v(ins[3]); ops += 1
            elif op == 'or': r[ins[1]] = v(ins[2]) | v(ins[3]); ops += 1
            elif op == 'xor': r[ins[1]] = v(ins[2]) ^ v(ins[3]); ops += 1
            elif op == 'shl': r[ins[1]] = (v(ins[2]) << ins[3]) & WORD; ops += 1
            elif op == 'shr': r[ins[1]] = v(ins[2]) >> ins[3]; ops += 1
            elif op == 'ld': r[ins[1]] = s.load(v(ins[2])); ops += 1
            elif op == 'ldi': r[ins[1]] = mem.get(ins[2], 0); ops += 1
            elif op == 'sti': mem[ins[1]] = v(ins[2]); ops += 1
            elif op == 'li': r[ins[1]] = ins[2]; ops += 1
            elif op == 'st': s.store(v(ins[1]), v(ins[2])); ops += 1
            elif op == 'bz': ops += 2; pc = lab[ins[2]] if v(ins[1]) == 0 else pc
            elif op == 'bnz': ops += 2; pc = lab[ins[2]] if v(ins[1]) != 0 else pc
            elif op == 'bne': ops += 2; pc = lab[ins[3]] if v(ins[1]) != v(ins[2]) else pc
            elif op == 'jmp': ops += 1; pc = lab[ins[1]]
            elif op == 'rand': r[ins[1]] = s.rw.pop(0); ops += 1
            elif op == 'f38':
                s.units += 1; m0 = [r[x] for x in ins[1]]; s.m0 = m0
                cv = s.cvforce if s.cvforce is not None else compress(IV, m0); s.cv = cv
                for x, y in zip(ins[2], cv): r[x] = y
            elif op == 'succ': s.succ = (ins[1], v(ins[2])); s.succ_ops = s.ops + ops; break
            elif op == 'halt_ok': break
            elif op == 'obs': s.obs.append(v(ins[1]))
            elif op == 'mark': s.marks.append(ins[1]); s.mark_ops.append((ins[1], s.ops + ops))
        s.ops += ops

MI.IMM = True; vt38.Machine = MI; Machine = MI
cs = vt38.prog_costs(); cs['EPI'] = 24; cs['P0'] -= 5          # prog_costs subtracts the epilogue 19; with immediates it is 24 (four rsub and the bne against the group count)
cs['PASS_ENTRY'] = 3; cs['BLOCK_FIXED'] = cs['GROUP4'] / 4        # the bne FL, 2 of the pass entry carries an immediate
print('online costs, immediates charged:', cs)
from vtpre import *
class MachineP(MI):
    def load(s, addr):
        if addr in s.mem: return s.mem[addr]
        t = addr >> 150
        return s.tab[addr] if t in (3, 4) and addr in s.tab else 0
os.makedirs(RUNS, exist_ok=True)
sys.argv = ['t_pre1.py']; ns = dict(globals()); ns['__name__'] = 'x'
src = open(os.path.join(SRC, 't_pre1.py')).read().replace("'../runs/pre1.json'", repr(os.path.join(RUNS, 'pre1_imm.json')))
with contextlib.redirect_stdout(io.StringIO()): exec(compile(src, 't_pre1.py', 'exec'), ns)
p1 = json.load(open(os.path.join(RUNS, 'pre1_imm.json')))
sys.argv = ['t_pre_d.py', VT, RUNS]; ns = dict(globals()); ns['__name__'] = 'x'
src = open(os.path.join(SRC, 't_pre_d.py')).read()
buf = io.StringIO()
with contextlib.redirect_stdout(buf): exec(compile(src, 't_pre_d.py', 'exec'), ns)
print('preprocessing bodies, immediates charged:')
q1 = json.load(open(os.path.join(RUNS, 'pre1.json'))); p1.update(LIVE_ops=q1['LIVE_ops'], LIVE_g=q1['LIVE_g']); p2 = json.load(open(os.path.join(RUNS, 'pre2.json')))
print(' pre1', p1); print(' pre2', p2)
from ledger38 import ledger
o = ledger(show=False, costs=cs, p1=p1, p2=p2)
print('ledger with immediates charged: time_log2 %.5f  log2_T %.6f' % (o['time_log2'], o['log2_T']))
