'''Python wrapper for the C block harness (Windows Python drives the WSL binary; also works inside Linux).

    from harness import Harness
    H = Harness()                                   # loads configs.json (133 base configurations)
    rs = H.apply_batch([(cfg, 'D', mask), ...])     # mask = list of XOR words in frame order (11 / 10 / 14 words)
    r = rs[0]; r['damage_names'], r['zero_damage'], r['steer'], r['dK1'], r['fast']
    H.apply_ref(cfg, 'D', mask)                     # same result from the pure-Python reference (organizer blake3.py)
    H.block(frame, {'S14': 1 << 5, 'C0.b1': 3})     # build a mask from {coordinate name: bits}
'''
import sys, os, json, subprocess, platform
sys.dont_write_bytecode = True
from common import (HERE, FRAMES, FRAME_ID, OBS_FIELDS, DAMAGE_BITS, INFO_BITS, STEER, ref_apply, steering_of, M)

def lin(p):
    p = os.path.abspath(p)
    return '/mnt/' + p[0].lower() + p[2:].replace('\\', '/') if platform.system() == 'Windows' else p
BIN = os.path.join(HERE, 'harness')

def names(bits, table): return [n for k, n in enumerate(table) if bits >> k & 1]

class Harness:
    def __init__(self, configs=os.path.join(HERE, 'configs.json'), txt=os.path.join(HERE, 'configs.txt')):
        self.cfgs = json.load(open(configs)); self.txt = txt
    def block(self, frame, bits):
        m = [0] * len(FRAMES[frame])
        for k, x in bits.items(): m[FRAMES[frame].index(k)] ^= x & M
        return m
    def _run(self, *args):
        cmd = [lin(BIN)] + [str(a) for a in args]
        if platform.system() == 'Windows': cmd = ['wsl', '-d', 'Ubuntu', '--'] + cmd
        return subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    def apply_batch(self, cases, work=None):
        '''cases: list of (config index, frame 'D'|'O'|'R', mask words). Returns one dict per case.'''
        work = work or HERE
        cpath, opath = os.path.join(work, '_cases.txt'), os.path.join(work, '_out.txt')
        with open(cpath, 'w', newline='\n') as f:
            for n, (ci, fr, m) in enumerate(cases):
                assert len(m) == len(FRAMES[fr])
                f.write('%d %d %s %s\n' % (n, ci, fr, ' '.join('%08x' % x for x in m)))
        self._run('apply', lin(self.txt), lin(cpath), lin(opath))
        out = []
        for line, (ci, fr, m) in zip(open(opath), cases):
            out.append(self.decode(line, ci))
        return out
    def decode(self, line, ci):
        full, fast = line.split('|')
        p = full.split(); q = fast.split()
        now = dict(zip(OBS_FIELDS, [int(x, 16) for x in p[4:]]))
        base = self.cfgs[ci]['obs']; dmg = int(p[1], 16); info = int(p[2], 16)
        st = steering_of(base, now)
        return dict(case=int(p[0]), damage=dmg, info=info, chk=int(p[3], 16), now=now,
                    damage_names=names(dmg, DAMAGE_BITS), info_names=names(info, INFO_BITS), zero_damage=dmg == 0,
                    steer={k: st[k] for k in STEER}, dK1=st['dK1'], hwK1=st['hwK1'],
                    dE3=[now[k] ^ base[k] for k in ('Y3', 'Y4', 'Y9', 'Y14', 'w8')],
                    fast=dict(damage=int(q[0], 16), T1=int(q[1], 16), K1=[int(x, 16) for x in q[2:6]]))
    def apply_ref(self, ci, frame, mask):
        dmg, info, chk, now = ref_apply(self.cfgs[ci], frame, mask)
        st = steering_of(self.cfgs[ci]['obs'], now)
        return dict(damage=dmg, info=info, chk=chk, now=now, damage_names=names(dmg, DAMAGE_BITS),
                    zero_damage=dmg == 0, steer={k: st[k] for k in STEER}, dK1=st['dK1'], hwK1=st['hwK1'])
    def bench(self, n=2000000): return self._run('bench', lin(self.txt), n)
    def census(self): return self._run('census', lin(self.txt))
