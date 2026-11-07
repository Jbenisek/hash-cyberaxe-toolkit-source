import sys, json
sys.path.insert(0, 'tests'); sys.path.insert(0, r'../../../3rd_openai_workspace/luna3')
from fh import *
import P3_22_bsgs as b
for name in ['ddf_g1000_natural_2', 'ddf_g1000_natural_3']:
    g = to_poly(read_poly('tests/data/%s.bin' % name)); d = g.degree()
    resid, costs = b.ks_strip_small_factors(g, P, d // 2)
    rows = costs['block_rows']
    luna = []; tot = 0
    for r in rows: tot += r['removed_degree']; luna.append(tot)
    o, e, rc = run_wsl(['ddf', '--g', 'tests/data/%s.bin' % name, '--check-every', '1', '--no-abort', '--check-from', '0', '--out', 'out/luna_t'])
    eng = [json.loads(x) for x in o.splitlines()]
    cps = [x['gcd_degree'] for x in eng if x['stage'] == 'checkpoint']
    done = [x for x in eng if x['stage'] == 'done'][0]
    print(luna, cps); print(name, 'l', costs['l'], 'blocks', costs['blocks'], 'luna residual', resid.degree(), 'engine residual', done['residual_degree'],
          'cumulative removed per block identical:', cps[:len(luna)] == luna and (len(luna) == len(cps) or luna[-1] == d))
