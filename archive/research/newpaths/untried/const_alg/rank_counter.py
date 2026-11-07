#!/usr/bin/env python3
r"""GAPS section 2 row 1 (const x alg on the counter base), step 1: rank every scored pin by the COUNTER objective

    C_ctr(pin) = max over beta of part(beta) x 2^k(beta)      (units 2^-128 per trial)

(the counter solve prescribes one beta, so its 2^-k is not paid by trials), and score it with the CENSUS one formula
    time_log2 = log2(0.5) + 128 - log2(C / m) + log2(ops / 430) + 0.02 + penalty
with m = 2.0 (ours; 1.4 = the board's), ops = 6.5 (H8's counted counter machine; a GUESS for every other pin), and
penalty 0 (a length pair without forced bytes).

Read only (nothing written outside this folder; bytecode writing off):
  research\catalogue\census\pins.py          (imported: the pin list and its per-beta file names)
  research\paths\paths_lib.py                (imported: walks(), the valid betas of a D11, and rol())
  the per-beta files that pins.py names, plus the second per-beta file of H8, L6a and L16a
  for the pins WITHOUT a per-beta file, the screens named in research\paths\ATLAS.md Table 1b:
     research\night\main\lx_totals.txt        (300 lightest betas: every beta with mass, "beta k positive part")
     research\night\main\cand_exact_lx.txt    (the pin search's own beta and its exact part; k computed here)
     astra-jobs\~archvie\...\task1_pins\out\totals.txt   (L8c: server, 1,000 lightest betas, heaviest beta)
Writes: rank_counter_out.txt, rank_counter.csv (this folder).
  python -B rank_counter.py
"""

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

import math
import os
import re
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
RES = _hca_public_path_text('__HCA_WORKSPACE__/research')
sys.path.insert(0, os.path.join(RES, 'catalogue', 'census'))
sys.path.insert(0, os.path.join(RES, 'paths'))
import pins as P          # noqa: E402  census pins.py
import paths_lib as L     # noqa: E402

M = 0xFFFFFFFF
SERVER = os.path.join(_hca_public_path_text('__HCA_WORKSPACE__/astra-jobs\\~archvie\\server_tasks_2026-10-06'),
                      r'HashSmash_Opus_Handoff_2026-10-06_updated\server_tasks_2026-10-06\task1_pins\out\totals.txt')
EXTRA = {   # second per-beta files (pins.py names one per pin)
    'H8': [r'night\main\pinH8_830303cf.total'],
    'L6a': [r'paths\counts\L6a_parts.txt'],
    'L16a': [r'paths\counts\L16a_parts.txt'],
    'L4b': [r'paths\counts\L4b_parts.txt'],      # the k <= 14 recount: empty (R 0 over k <= 14)
}
H8_SUBCLASS = 67698688.0  # CENSUS line 42: the counter lever 84.96 uses H8's sub-class C15, beta k = 11


def score(c, m=2.0, ops=6.5, pen=0.0):
    return math.log2(0.5) + 128 - math.log2(c / m) + math.log2(ops / 430) + 0.02 + pen


def kof(beta):
    return bin(L.rol(beta, 12) & 0x7FFFFFFF).count('1')


def tsv():
    return L.read_pins()


def disp(f):
    return os.path.relpath(f, RES) if os.path.isabs(f) else f


def new_file(name):
    """the per-beta file computed in this folder (ctr_count.py report -> counts/NAME_parts.txt), or None"""
    f = os.path.join(HERE, 'counts', f'{name}_parts.txt')
    return f if os.path.exists(f) else None


def read_rows(relpath):
    """[(beta, k, part)] of a per-beta file, parsed as pins.best_counter_mass parses it"""
    rows = []
    path = relpath if os.path.isabs(relpath) else os.path.join(RES, relpath)
    if not os.path.exists(path):
        return None
    for line in open(path, encoding='ascii', errors='replace'):
        s = line.strip()
        if not s or s.startswith('#'):
            continue
        tok = s.split()
        if not re.fullmatch(r'[0-9a-f]{8}', tok[0]) or len(tok) < 3:
            continue
        try:
            k = int(tok[1])
        except ValueError:
            continue
        nums = []
        for t in tok[2:]:
            try:
                nums.append(float(t))
            except ValueError:
                break
        if not nums:
            continue
        if relpath.endswith('.total'):
            if len(nums) < 2:
                continue
            part = nums[1]
        elif 'L6a_total' in relpath or 'parts2' in relpath:
            part = nums[0]
        else:
            part = nums[1] if len(nums) >= 2 else nums[0]
        rows.append((int(tok[0], 16), k, part))
    return rows


def screens(pins):
    """per pin: list of (source, beta, k, part) from the night's screens and the server's totals"""
    out = {n: [] for n in pins}
    key = {(p['D3'], p['D11'], p['delta'], p['Y3'], p['Y11'], p['eta']): n for n, p in pins.items()}
    pinkey = {tuple(p[c] for c in ('X3', 'X7', 'X11', 'X15', 'W4', 'W13')): n for n, p in pins.items()}
    lt = os.path.join(RES, r'night\main\lx_totals.txt')
    for ln, line in enumerate(open(lt, encoding='ascii', errors='replace'), 1):
        f = line.split('|')
        if len(f) < 3:
            continue
        t = f[1].split()
        if len(t) != 6:
            continue
        n = key.get(tuple(int(x, 16) for x in t))
        if n is None or 'exact class rate' not in line:
            continue
        rest = line.split('exact class rate', 1)[1].strip().split(None, 1)
        if len(rest) < 2:
            continue
        for ent in rest[1].split(';'):
            e = ent.split()
            if len(e) == 4 and re.fullmatch(r'[0-9a-f]{8}', e[0]):
                out[n].append((f'lx_totals.txt:{ln} (300 lightest)', int(e[0], 16), int(e[1]), float(e[3])))
    ce = os.path.join(RES, r'night\main\cand_exact_lx.txt')
    for ln, line in enumerate(open(ce, encoding='ascii', errors='replace'), 1):
        mpin = re.search(r'pin ([0-9a-f,]{53})', line)
        mb = re.search(r'beta ([0-9a-f]{8})', line)
        mx = re.search(r'exact ([0-9.]+)', line)
        if not (mpin and mb and mx):
            continue
        n = pinkey.get(tuple(int(x, 16) for x in mpin.group(1).split(',')))
        if n is None:
            continue
        b = int(mb.group(1), 16)
        out[n].append((f'cand_exact_lx.txt:{ln} (search beta)', b, kof(b), float(mx.group(1))))
    if os.path.exists(SERVER):
        for line in open(SERVER, encoding='ascii', errors='replace'):
            mpin = re.match(r'([0-9a-f,]{53}) ', line)
            mh = re.search(r'heaviest ([0-9a-f]{8}) ([0-9.]+)', line)
            if not (mpin and mh):
                continue
            n = pinkey.get(tuple(int(x, 16) for x in mpin.group(1).split(',')))
            if n is None:
                continue
            b = int(mh.group(1), 16)
            out[n].append(('server task1_pins totals.txt (1,000 lightest, heaviest)', b, kof(b), float(mh.group(2))))
    return out


def main():
    pins = tsv()
    lines, csv = [], ['pin,source,beta,k,part,C_ctr,log2_C_ctr,ctr_score_m2,ctr_score_m1.4,root_R,maxk_counted,n_betas,label']
    lines.append('CONST x ALG on the counter base: every scored pin by C_ctr = max over beta of part x 2^k (units 2^-128 per trial)')
    lines.append('score = log2(0.5) + 128 - log2(C/m) + log2(6.5/430) + 0.02 (CENSUS one formula, penalty 0); m 2.0 and 1.4')
    lines.append('')
    # calibration against CENSUS section 0 item 3
    cal = [('H8 sub-class (2^11 x 67,698,688)', 2 ** 11 * H8_SUBCLASS, 84.96), ('L6c (e91e11a6, k 14, 1,863,680)', 2 ** 14 * 1863680.0, 87.14),
           ('L16a (f990e10a, k 14, 2,355,712)', 2 ** 14 * 2355712.0, 86.80)]
    lines.append('Calibration (CENSUS section 0 item 3):')
    for name, c, want in cal:
        lines.append(f'  {name}: {score(c):.2f} (CENSUS {want:.2f})')
    lines.append('')
    have, lack, made = [], [], []
    ranked = []
    kcheck_bad = 0
    kcheck_n = 0
    for name, consts, R, status, rel in P.PINS:
        if R is None:
            continue
        nf = new_file(name)
        if nf:
            made.append(name)
        files = ([rel] if rel else []) + EXTRA.get(name, []) + ([nf] if nf else [])
        best = None
        cover = []
        for f in files:
            rows = read_rows(f)
            if rows is None:
                cover.append(f'{f}: MISSING')
                continue
            for b, k, part in rows:
                if name in pins:
                    kcheck_n += 1
                    if kof(b) != k:
                        kcheck_bad += 1
            pos = [(part * 2 ** k, b, k, part) for b, k, part in rows if part > 0]
            cover.append(f'{disp(f)}: {len(rows)} betas, {len(pos)} with a part, max k counted {max((k for b, k, p in rows), default="-")}')
            for v in pos:
                if best is None or v[0] > best[0]:
                    best = v + (f,)
        pb = P.best_counter_mass(rel) if rel else None
        if rel:
            have.append(name)
        else:
            lack.append(name)
        ranked.append((name, R, status, rel, best, pb, cover))
    lines.append(f'k check (k column = weight of ROL(beta, 12) below bit 31) over every per-beta line: {kcheck_n - kcheck_bad} of {kcheck_n} agree')
    lines.append('')
    lines.append(f'Scored pins with a per-beta file ({len(have)}): ' + ', '.join(have))
    lines.append(f'Scored pins WITHOUT one ({len(lack)}): ' + ', '.join(lack))
    lines.append(f'Per-beta files computed in this folder (counts\\NAME_parts.txt, ctr_count.py): ' + (', '.join(made) or 'none yet'))
    lines.append('')
    # ---- table 1: pins with a per-beta file (named by pins.py, or computed here)
    rows1 = []
    for name, R, status, rel, best, pb, cover in ranked:
        if not rel and name not in made:
            continue
        if best is None:
            rows1.append((float('inf'), name, R, None, cover, pb))
            continue
        c, b, k, part, f = best
        rows1.append((score(c), name, R, best, cover, pb))
    rows1.sort()
    lines.append('TABLE 1. Pins with a per-beta file, ranked by the counter score (COMPUTED max from the files; DERIVED score; GUESS ops 6.5)')
    lines.append('  rank pin    best beta  k   part                 C_ctr = part x 2^k        log2 C  ctr m2.0  ctr m1.4  root R          file of the max')
    for i, (sc, name, R, best, cover, pb) in enumerate(rows1, 1):
        if best is None:
            lines.append(f'  {i:>3}  {name:<6} no beta with a part in its files')
            csv.append(f'{name},per-beta,-,-,0,0,-,-,-,{R},-,-,COMPUTED')
            continue
        c, b, k, part, f = best
        lines.append(f'  {i:>3}  {name:<6} {b:08x}  {k:>2}  {part:>18,.2f}  {c:>24,.0f}  {math.log2(c):6.3f}  {sc:7.2f}  {score(c, m=1.4):7.2f}  {R:>14,.1f}  {disp(f)}')
        csv.append(f'{name},{disp(f)},{b:08x},{k},{part:.8f},{c:.1f},{math.log2(c):.4f},{sc:.3f},{score(c, m=1.4):.3f},{R},,,COMPUTED max; DERIVED score; GUESS ops')
        if pb is not None and abs(pb[0] - c) > 1e-6 * c and f == ranked_rel(ranked, name):
            lines.append(f'        (pins.best_counter_mass on its own file: {pb[0]:,.0f})')
    lines.append('  H8 at 84.96 in CENSUS is the sub-class C15 (2^11 x 67,698,688); the whole class above gives 84.88.')
    lines.append('')
    lines.append('  coverage of the per-beta files (the max is a LOWER BOUND wherever SAT betas are not counted):')
    for name, R, status, rel, best, pb, cover in ranked:
        if rel or name in made:
            for cv in cover:
                lines.append(f'    {name:<5} {cv}')
    lines.append('')
    # ---- table 2: pins without a per-beta file: screened per-beta values
    scr = screens(pins)
    rows2 = []
    for name, R, status, rel, best, pb, cover in ranked:
        if rel and name != 'L4b':
            continue
        ent = scr.get(name, [])
        if not ent:
            rows2.append((float('inf'), name, R, None, 0))
            continue
        top = max(ent, key=lambda e: e[3] * 2 ** e[2])
        rows2.append((score(top[3] * 2 ** top[2]), name, R, top, len(ent)))
    rows2.sort()
    lines.append('TABLE 2. Pins WITHOUT a per-beta file (and L4b, whose k <= 14 recount is empty): best SCREENED beta by part x 2^k')
    lines.append('  (COMPUTED from the screen files: part as printed there, k computed from the beta; DERIVED score; a LOWER BOUND on C_ctr)')
    lines.append('  rank pin    best beta  k   part                 C_ctr = part x 2^k        log2 C  ctr m2.0  root R(screen)  betas seen  source')
    for i, (sc, name, R, top, nent) in enumerate(rows2, 1):
        if top is None:
            lines.append(f'  {i:>3}  {name:<6} no screened beta found')
            continue
        src, b, k, part = top
        c = part * 2 ** k
        lines.append(f'  {i:>3}  {name:<6} {b:08x}  {k:>2}  {part:>18,.2f}  {c:>24,.0f}  {math.log2(c):6.3f}  {sc:7.2f}  {R:>14,.1f}  {nent:>5}  {src}')
        csv.append(f'{name},{src},{b:08x},{k},{part:.8f},{c:.1f},{math.log2(c):.4f},{sc:.3f},{score(c, m=1.4):.3f},{R},,{nent},COMPUTED screen; DERIVED score; LOWER BOUND')
    lines.append('')
    lines.append('  every screened beta of these pins (source, beta, k, part, part x 2^k, score):')
    for name in sorted(scr):
        if not scr[name] or (name in have and name != 'L4b'):
            continue
        for src, b, k, part in sorted(scr[name], key=lambda e: -e[3] * 2 ** e[2]):
            if part <= 0:
                continue
            c = part * 2 ** k
            lines.append(f'    {name:<5} {b:08x} k {k:>2} part {part:>16,.2f}  x2^k {c:>22,.0f}  score {score(c):6.2f}  {src}')
    # ---- table 3: NEW pins found here by the counter-objective solver (pins_new.tsv), with their per-beta files
    pn = os.path.join(HERE, 'pins_new.tsv')
    if os.path.exists(pn):
        newp = L.read_pins(pn)
        lines.append('')
        lines.append('TABLE 3. NEW pins found here (trailmin5_ctr.py, pins_new.tsv), per-beta files made here (COMPUTED max; DERIVED score; GUESS ops)')
        lines.append('  pin    best beta  k   part                 C_ctr = part x 2^k        log2 C  ctr m2.0  ctr m1.4  R found          file')
        for name in newp:
            nf = new_file(name)
            rows = read_rows(nf) if nf else None
            if not rows:
                lines.append(f'  {name:<6} no per-beta file yet')
                continue
            for b, k, part in rows:
                kcheck_n += 1
                if kof(b) != k:
                    kcheck_bad += 1
            c, b, k, part = max((part * 2 ** k, b, k, part) for b, k, part in rows if part > 0)
            R = sum(part for b, k, part in rows)
            lines.append(f'  {name:<6} {b:08x}  {k:>2}  {part:>18,.2f}  {c:>24,.0f}  {math.log2(c):6.3f}  {score(c):7.2f}  {score(c, m=1.4):7.2f}  {R:>14,.1f}  {disp(nf)}')
            lines.append(f'         root, for comparison: R found {R:,.1f} -> {score(R, ops=7.7):.2f} (CENSUS root ops 7.7, GUESS)')
            csv.append(f'{name},{disp(nf)},{b:08x},{k},{part:.8f},{c:.1f},{math.log2(c):.4f},{score(c):.3f},{score(c, m=1.4):.3f},{R},,{len(rows)},COMPUTED max; DERIVED score; GUESS ops')
        lines.append(f'  k check over the new files: {kcheck_n - kcheck_bad} of {kcheck_n} lines agree (all files)')
    txt = '\n'.join(lines) + '\n'
    open(os.path.join(HERE, 'rank_counter_out.txt'), 'w', encoding='ascii').write(txt)
    open(os.path.join(HERE, 'rank_counter.csv'), 'w', encoding='ascii').write('\n'.join(csv) + '\n')
    print(txt)


def ranked_rel(ranked, name):
    for n, R, status, rel, best, pb, cover in ranked:
        if n == name:
            return rel
    return None


if __name__ == '__main__':
    main()
