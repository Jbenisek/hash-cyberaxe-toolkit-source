# intake_read.py SLOT... : status fields of the organizer intake report of each staged slot
import json, sys, os, time
for s in sys.argv[1:]:
    f = os.path.expanduser('~/hashsmash/yukon/pos_%s/pareto/.yukon/work/tracks/sha256-pareto/intake-report.json' % s.lower())
    d = json.load(open(f)); print('==', s, time.ctime(os.path.getmtime(f)), 'top keys', list(d)[:12])
    def w(o, p=''):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in ('status', 'errors', 'warnings', 'findings', 'valid', 'ok', 'reason', 'result', 'time_log2', 'mechanical_status', 'outcome'):
                    print(' ', p + '/' + k, json.dumps(v)[:240])
                w(v, p + '/' + k)
        elif isinstance(o, list):
            for i, v in enumerate(o[:60]): w(v, p + '/%d' % i)
    w(d)
