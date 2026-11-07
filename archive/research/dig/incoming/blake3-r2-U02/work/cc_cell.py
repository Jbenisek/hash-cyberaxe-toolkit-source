#!/usr/bin/env python3
# U02 helper: beta* (18b0e098) exact class part for one (Y3, Y11) cell, reusing pkg17/count/count_class.py unchanged
# (its width-6 self-test is the validation; the control is Y3=8127c181,Y11=7af77f38 -> 71,698,432 / S-part 67,633,152).

# Publication path adapter: resolve data paths from the extracted source tree.
def _hca_public_path_text(value):
    if "__HCA_WORKSPACE__/" not in value:
        return value
    import os as _hca_os
    from pathlib import Path as _hca_Path
    root = _hca_os.environ.get("HASHCYBERAXE_WORKSPACE")
    if root is None:
        here = _hca_Path(__file__).resolve().parent
        root = next((str(p) for p in (here, *here.parents) if (p / "research").is_dir()), None)
    if root is None:
        raise FileNotFoundError("Extract the research source tree, or set HASHCYBERAXE_WORKSPACE to its archive directory.")
    return value.replace("__HCA_WORKSPACE__/", str(_hca_Path(root).resolve()).replace("\\", "/") + "/")

import sys, time, json
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/pkg17/count'))
import count_class as cc
M = 0xffffffff
D3, D11, DELTA = 0xfdb77cfd, 0x0a08818b, (0x97475638 - 0x97475640) & M
S_TAUS = {0x285020a0, 0x185020a0, 0x385020a0, 0x175020a0, 0x685020a0, 0x275020a0}
def run(Y3, Y11, beta=0x18b0e098):
    Y3B, Y11B = (Y3 + D3) & M, (Y11 + D11) & M
    Y4s = [((0x030c0303 | f) - Y3) & M for f in cc.subs(~0x03cf8303 & M)]
    c = cc.Inst(32, 16, 12, 8, 7, Y3, Y3B, Y11, Y11B, DELTA, 0x830303cf, Y4s, [])
    assert len(Y4s) == 524288 and all(cc.ror(c, ((Y3 + y) ^ (Y3B + y)) & M, 16) == c.eta for y in Y4s)
    t0 = time.perf_counter()
    rows, tot, totA = cc.beta_part(c, beta, show=lambda *a: None)
    sS = sum(L * n3 for tau, eps, L, n3, n3a in rows if tau in S_TAUS)
    out = dict(Y3=f'{Y3:08x}', Y11=f'{Y11:08x}', beta=f'{beta:08x}', outcomes=len(rows),
               whole_over_2_83=[tot >> 83, tot % (1 << 83)], S_over_2_83=[sS >> 83, sS % (1 << 83)],
               rows=[[f'{t:08x}', f'{e:08x}', L * n3 >> 81] for t, e, L, n3, n3a in sorted(rows)],
               seconds=round(time.perf_counter() - t0, 1))
    print(json.dumps(out), flush=True)
if __name__ == '__main__':
    for a in sys.argv[1:]:
        y3, y11 = a.split(',')
        run(int(y3, 16), int(y11, 16))
