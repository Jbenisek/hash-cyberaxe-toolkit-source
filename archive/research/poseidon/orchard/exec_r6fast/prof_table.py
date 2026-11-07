"""Summarise the PROFROW lines of a profile run (stderr of a -DPROF build).
usage: python3 prof_table.py ERRFILE [TAG]
Columns per region: serial ms (main thread alone), dispatch ms (main thread inside a dispatch), busy ms (sum over all threads of chunk time),
and the effective threads in the dispatches (busy / dispatch).  The last report block in the file is used (after-D or end)."""
import sys, collections
lines = open(sys.argv[1], errors='replace').read().splitlines()
# take the last report block
starts = [i for i, l in enumerate(lines) if l.startswith('PROF ') and 'threads=' in l]
if not starts:
    print('no PROF block'); sys.exit(1)
blk = lines[starts[-1]:]
head = blk[0]
rows = []
for l in blk[1:]:
    if not l.startswith('PROFROW '): continue
    name, a, ser, wall, busy, capw, nd = l[8:].split('|')
    rows.append((name, int(a), int(ser), int(wall), int(busy), int(capw), int(nd)))
print(head)
tot_ser = sum(r[2] for r in rows); tot_wall = sum(r[3] for r in rows); tot_busy = sum(r[4] for r in rows)
print(f'main-thread time: serial {tot_ser/1000:.1f} s, in dispatches {tot_wall/1000:.1f} s, total {(tot_ser+tot_wall)/1000:.1f} s; busy thread-time {tot_busy/1000:.1f} s')
print(f'work (serial + busy) {(tot_ser+tot_busy)/1000:.1f} thread-s; serial share of work {tot_ser/(tot_ser+tot_busy):.3f}; wall share of serial {tot_ser/(tot_ser+tot_wall):.3f}')
by = collections.OrderedDict()
for r in rows:
    d = by.setdefault(r[0], [0, 0, 0, 0])
    d[0] += r[2]; d[1] += r[3]; d[2] += r[4]; d[3] += r[6]
print('\n| region | serial s | dispatch s | busy thread-s | eff. threads in dispatch | dispatches | share of wall | share of work |')
print('|---|---:|---:|---:|---:|---:|---:|---:|')
W = tot_ser + tot_wall; K = tot_ser + tot_busy
for k, d in by.items():
    eff = d[2] / d[1] if d[1] else 0
    print(f'| {k} | {d[0]/1000:.1f} | {d[1]/1000:.1f} | {d[2]/1000:.1f} | {eff:.2f} | {d[3]} | {(d[0]+d[1])/W:.3f} | {(d[0]+d[2])/K:.3f} |')
bya = collections.OrderedDict()
for r in sorted(rows, key=lambda r: r[1]):
    d = bya.setdefault(r[1], [0, 0, 0, 0])
    d[0] += r[2]; d[1] += r[3]; d[2] += r[4]; d[3] += r[6]
print('\n| row length log2 a (0 = outside transforms) | serial s | dispatch s | busy thread-s | eff. threads | share of wall |')
print('|---|---:|---:|---:|---:|---:|')
for a, d in bya.items():
    eff = d[2] / d[1] if d[1] else 0
    print(f'| {a} | {d[0]/1000:.1f} | {d[1]/1000:.1f} | {d[2]/1000:.1f} | {eff:.2f} | {(d[0]+d[1])/W:.3f} |')
# stage D by a
print('\n| stage D: region x a | serial s | dispatch s | busy s |')
print('|---|---:|---:|---:|')
for r in rows:
    if r[0].startswith('D') and (r[2] + r[3]) > 0.002 * W:
        print(f'| {r[0]} a={r[1]} | {r[2]/1000:.1f} | {r[3]/1000:.1f} | {r[4]/1000:.1f} |')
