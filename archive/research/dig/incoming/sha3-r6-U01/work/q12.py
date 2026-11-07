import sys, json, random, time, statistics as st
import sha3lab as L
from sha3lab import *


def setup(fmt):
    F = Forms(fmt)
    dirs = []
    conds = []   # (j, fam, state bit, required value)
    for j in range(32):
        d = (1 << j) | (1 << (320 + j))
        T = lin_image(fmt, d)
        pos = [p for p in range(1600) if (T >> p) & 1]
        assert len(pos) == 2, (j, pos)
        dirs.append((d, T, pos))
        for k, p in enumerate(pos):
            lane, z = divmod(p, 64)
            x, y = lane % 5, lane // 5
            up = 64 * ((x + 1) % 5 + 5 * y) + z
            dn = 64 * ((x - 1) % 5 + 5 * y) + z
            conds.append((j, 2 * k, up, 0))
            conds.append((j, 2 * k + 1, dn, 1))
    return F, dirs, conds


def eq_of(F, c):
    j, fam, p, val = c
    return F.rows[p], val ^ ((F.const >> p) & 1)


def measure(F, dirs, m, nrandz=0, rng=None, deep=False):
    A = to_lanes(F.const ^ lin_image(F.fmt, m))   # post theta,rho,pi state of message m
    O = chi(A)
    res = []
    D = []
    for (d, T, pos) in dirs:
        Tl = to_lanes(T)
        O2 = chi([a ^ b for a, b in zip(A, Tl)])
        dl = [a ^ b for a, b in zip(O, O2)]
        dv = to_int(dl)
        D.append(dv)
        r = dict(w=bin(dv).count('1'), ident=(dv == T), dv=dv)
        if deep:
            th = to_int(theta(dl))
            r['fp'] = bin(th).count('1')
            rp = to_int(rhopi(to_lanes(th)))
            cnt = {}
            for p in range(1600):
                if (rp >> p) & 1:
                    lane, z = divmod(p, 64)
                    key = (lane // 5, z)
                    cnt[key] = cnt.get(key, 0) + 1
            r['rows'] = len(cnt)
            r['two'] = sum(1 for v in cnt.values() if v >= 2)
            A1 = [a ^ (RC[0] if i == 0 else 0) for i, a in enumerate(O)]
            A2 = rhopi(theta(A1))
            A2b = [a ^ b for a, b in zip(A2, to_lanes(rp))]
            c2 = [a ^ b for a, b in zip(chi(A2), chi(A2b))]
            r['fp3'] = bin(to_int(theta(c2))).count('1')
        res.append(r)
    fails = 0
    for _ in range(nrandz):
        zmask = rng.getrandbits(32)
        Tz = 0
        exp = 0
        for j in range(32):
            if (zmask >> j) & 1:
                Tz ^= dirs[j][1]
                exp ^= D[j]
        O2 = chi([a ^ b for a, b in zip(A, to_lanes(Tz))])
        if to_int([a ^ b for a, b in zip(O, O2)]) != exp:
            fails += 1
    piv = {}
    rank = 0
    for v in D:
        while v:
            p = v.bit_length() - 1
            if p in piv:
                v ^= piv[p]
            else:
                piv[p] = v
                rank += 1
                break
    return res, fails, rank


def build_sys(F, conds, skip=()):
    S = Sys()
    stat = {'new': 0, 'dep': 0, 'incons': 0}
    for i, c in enumerate(conds):
        if i in skip:
            continue
        r, v = eq_of(F, c)
        stat[S.add(r, v)] += 1
    return S, stat


if __name__ == '__main__':
    out = {}
    rng = random.Random(20261012)
    for fmt in ('F64', 'F135'):
        t0 = time.time()
        F, dirs, conds = setup(fmt)
        zdep = sum(1 for c in conds for (d, T, pos) in dirs if parity(F.rows[c[2]] & d))
        distinct_bits = len(set(c[2] for c in conds))
        vary = set(p for (_, _, pos) in dirs for p in pos)
        overlap = len(vary & set(c[2] for c in conds))
        S, stat = build_sys(F, conds)
        o = dict(fmt=fmt, nvars=F.nv, n_conditions=len(conds), distinct_cond_bits=distinct_bits, rank=S.rank(), stat=stat,
                 zdep_forms=zdep, vary_cond_overlap=overlap)
        W = []; ident = 0; tot = 0; fails = 0; ranks = []; fp = []; rows = []; two = []; fp3 = []
        for s in range(300):
            m = S.sample(F.nv, rng)
            res, fl, rk = measure(F, dirs, m, nrandz=10, rng=rng, deep=(s < 120))
            fails += fl; ranks.append(rk)
            for r in res:
                W.append(r['w']); ident += r['ident']; tot += 1
                if 'fp' in r:
                    fp.append(r['fp']); rows.append(r['rows']); two.append(r['two']); fp3.append(r['fp3'])
        o['satisfied'] = dict(samples=300, dirs_checked=tot, weight_set=sorted(set(W)), identity_frac=ident / tot, affine_fails=fails,
                              affine_checks=3000, rank_min=min(ranks), fp_theta2_set=sorted(set(fp)), rows_set=sorted(set(rows)),
                              two_input_rows_set=sorted(set(two)), fp_theta3_mean=st.mean(fp3), fp_theta3_min=min(fp3), fp_theta3_max=max(fp3))
        W = []; fails = 0; ranks = []; ident = 0; tot = 0
        for s in range(100):
            m = rng.getrandbits(F.nv)
            res, fl, rk = measure(F, dirs, m, nrandz=10, rng=rng)
            fails += fl; ranks.append(rk)
            for r in res:
                W.append(r['w']); ident += r['ident']; tot += 1
        o['random_prefix'] = dict(samples=100, weight_mean=st.mean(W), weight_set=sorted(set(W)), identity_frac=ident / tot,
                                  affine_fails=fails, affine_checks=1000, rank_min=min(ranks))
        rows_q2 = []
        for i, c in enumerate(conds):
            S2, st2 = build_sys(F, conds, skip=(i,))
            dep = (S2.rank() == S.rank())
            row = dict(i=i, j=c[0], fam=c[1], pos=c[2], val=c[3], redundant=dep)
            if not dep:
                fl_t = 0; rk_min = 99; wj = []; distinct = set(); fpv = []; rowsv = []
                for s in range(60):
                    m = S2.sample(F.nv, rng)
                    res, fl, rk = measure(F, dirs, m, nrandz=10, rng=rng, deep=(s < 20))
                    fl_t += fl; rk_min = min(rk_min, rk)
                    wj.append(res[c[0]]['w']); distinct.add(res[c[0]]['dv'])
                    for r in res:
                        if 'fp' in r and r['w'] != 2:
                            fpv.append(r['fp']); rowsv.append(r['rows'])
                row.update(affine_fails=fl_t, affine_checks=600, rank_min=rk_min, w_dir_set=sorted(set(wj)),
                           frac_w3=sum(1 for w in wj if w != 2) / len(wj), distinct_dv_for_dir=len(distinct),
                           fp_when_viol=(sorted(set(fpv)) if fpv else None), rows_when_viol=(sorted(set(rowsv)) if rowsv else None))
            rows_q2.append(row)
        o['q2_rows'] = rows_q2
        fam_out = {}
        for fam in range(4):
            skip = tuple(i for i, c in enumerate(conds) if c[1] == fam)
            S2, _ = build_sys(F, conds, skip=skip)
            W = []; fl_t = 0; rk_min = 99
            for s in range(60):
                m = S2.sample(F.nv, rng)
                res, fl, rk = measure(F, dirs, m, nrandz=10, rng=rng)
                fl_t += fl; rk_min = min(rk_min, rk); W += [r['w'] for r in res]
            fam_out[fam] = dict(rank_after=S2.rank(), weight_mean=st.mean(W), weight_set=sorted(set(W)), affine_fails=fl_t,
                                affine_checks=600, rank_min=rk_min)
        o['q2_family_drop'] = fam_out
        nr = [r for r in rows_q2 if not r['redundant']]
        o['q2_summary'] = dict(n=len(rows_q2), redundant=sum(r['redundant'] for r in rows_q2), nonredundant=len(nr),
                               total_affine_fails=sum(r['affine_fails'] for r in nr), min_rank=min(r['rank_min'] for r in nr),
                               all_change_weight=all(r['frac_w3'] > 0 for r in nr), frac_w3_mean=st.mean(r['frac_w3'] for r in nr))
        o['secs'] = round(time.time() - t0, 1)
        out[fmt] = o
        print(fmt, json.dumps({k: v for k, v in o.items() if k != 'q2_rows'}, default=str), flush=True)
    json.dump(out, open('q12_out.json', 'w'), indent=1, default=str)
