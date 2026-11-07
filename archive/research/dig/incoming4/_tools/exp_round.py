import sys, json, time, random
from eng import *
random.seed(20261012)
IDX_OF = {'R0':0,'R1':1,'R2':2,'R3':3,'P1':4,'R60':60,'R61':61,'R62':62,'R63':63}

def eval_var(nk, rho, r, var):
    s = [nk, rho, CAPACITY]
    for idx in schedule(r):
        o = round_opts(idx, var)
        s = [(s[i] + (RC[idx][i] if o['arc'][i] else 0)) % P for i in range(3)]
        s = [pow(s[i],5,P) if o['sb'][i] else s[i] for i in range(3)]
        M = o['M']
        s = [sum(M[i][k]*s[k] for k in range(3)) % P for i in range(3)]
    return s[0]

def var_for(idx, L, layer):
    o = round_opts(idx, {})
    if layer == 'ARC':
        a = list(o['arc']); a[L] = 0; return {idx: dict(arc=tuple(a))}
    if layer == 'SBOX':
        sb = list(o['sb']); sb[L] = 1 - sb[L]; return {idx: dict(sb=tuple(sb))}   # toggle: drop if present, add if absent
    M = [list(r) for r in MDS]; M[L] = [1 if k == L else 0 for k in range(3)]
    return {idx: dict(M=tuple(tuple(r) for r in M))}

def trio(var):
    out = []
    for j in range(3):
        try:
            res = run_line(1, j, var)
        except Exception as e:
            res = dict(ok=False, why='exc '+repr(e)[:80])
        if res['ok']:
            out.append(dict(j=j, deg=res['deg'], lc_nonzero=res['lc'] != 0))
        else:
            out.append(dict(j=j, line=False, why=res['why']))
    return out

def hash_same(var, n=4):
    ok = 0
    for _ in range(n):
        nk, rho = random.randrange(P), random.randrange(P)
        ok += eval_var(nk, rho, 1, var) == hash_reduced(nk, rho, 1)
    return ok, n

if __name__ == '__main__':
    rounds = sys.argv[1:]
    res = {}
    for rn in rounds:
        idx = IDX_OF[rn]
        for L in range(3):
            for layer in ('ARC','SBOX','MDS'):
                t=time.time()
                var = var_for(idx, L, layer)
                key = '%s.L%d.%s' % (rn, L, layer)
                res[key] = dict(lines=trio(var), hash_same=hash_same(var), sec=round(time.time()-t,1))
                print(key, res[key], flush=True)
    json.dump(res, open('round_%s.json' % '_'.join(rounds), 'w'), indent=1)
