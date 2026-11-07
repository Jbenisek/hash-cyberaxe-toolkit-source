#!/usr/bin/env python3
"""peek_run.py PID BINARY : read-only look at a running single (non-PIE static): open stage, trial number, op counters, arena high-water.
Reads /proc/PID/mem only (no ptrace stop, no signal). Local single-thread binaries; for the mt build the counters of the main thread only."""
import sys, struct, subprocess
pid, binp = int(sys.argv[1]), sys.argv[2]
sym = {}
for l in subprocess.check_output(['nm', binp]).decode().splitlines():
    f = l.split()
    if len(f) == 3: sym.setdefault(f[2], int(f[0], 16))
m = open('/proc/%d/mem' % pid, 'rb')
def rd(a, n): m.seek(a); return m.read(n)
def q(name, k=1):
    try: return struct.unpack('<%dQ' % k, rd(sym[name], 8 * k))
    except OSError: return (None,) * k   # not readable (e.g. thread-local block in the mt build)
out = {}
if 'cur_trial' in sym: out['trial'] = struct.unpack('<i', rd(sym['cur_trial'], 4))[0]
if 'cur_name' in sym:
    p = q('cur_name')[0]
    out['stage'] = rd(p, 48).split(b'\0')[0].decode(errors='replace') if p else None
if 'fp_cnt' in sym: out['fp_add_sub_mul_sqr'] = q('fp_cnt', 4)
if 'X' in sym: out['X_ld_st_ctl_rnd_perm'] = q('X', 5)
for k in ('arena_hwm', 'mem_cur', 'mem_peak'):
    if k in sym: out[k] = q(k)[0]
if 'fp_cnt' in sym and 'X' in sym:
    a = q('fp_cnt', 4); x = q('X', 5)
    if None not in a + x: out['ops_now'] = sum(a) + sum(x)
print(out)
