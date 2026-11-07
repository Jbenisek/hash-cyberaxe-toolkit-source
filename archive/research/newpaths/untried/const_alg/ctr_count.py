#!/usr/bin/env python3
r"""The atlas per-beta count pipeline of research\paths, imported UNCHANGED, with every output redirected into this
folder (research only; nothing filed):
    scratch  research\paths: ~/hashsmash/paths/NAME/   ->  const_alg/scratch/NAME/
    reports  research\paths: research/paths/counts/    ->  const_alg/counts/   (NAME_parts.txt = the per-beta file)
Steps (the same functions run_count.sh calls; WSL python3):
    ctr_count.py filter   NAME PAR KMAX                  paths_filter.main   (h8_pair_list, list-only)
    ctr_count.py sys      NAME WORKERS TIMEOUT SAMPLE KMAX  paths_sys.main run  (kissat -q --time=TIMEOUT per beta)
    ctr_count.py satcount NAME PAR TIMEOUT               paths_report.cmd_satcount (h8_pair_calc_batch, time limit)
    ctr_count.py report   NAME                           paths_report.cmd_report
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

import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
PATHS = Path(_hca_public_path_text('__HCA_WORKSPACE__/research/paths'))
sys.path.insert(0, str(PATHS))
import paths_lib as L          # noqa: E402,F401
import paths_count as C        # noqa: E402
import paths_filter as FL      # noqa: E402
import paths_sys as SY         # noqa: E402
import paths_report as RP      # noqa: E402

SCR = HERE / 'scratch'
C.SCR = SCR
C.OUT = HERE / 'counts'
FL.SCR = SCR

# pins found here by the counter-objective solver are read from pins_new.tsv (same columns as research/paths/pins.tsv,
# which stays untouched); every module above looks pins up through paths_lib.read_pins
_read_pins = L.read_pins


def _read_pins_plus(path=None):
    out = _read_pins(path)
    extra = HERE / 'pins_new.tsv'
    if path is None and extra.exists():
        out.update(_read_pins(extra))
    return out


L.read_pins = _read_pins_plus


def cmd_satfirst(name, par, timeout, firsts, last):
    """paths_report.cmd_satcount with its first_betas ordering taken from the command line (research/paths/
    first_betas.txt has no line for a pin found here): SAT betas nearest to FIRSTS first, the betas in LAST at the
    end (one of them held a process for the whole time limit before). Same calculator call, same 'sat' raw files."""
    import time
    from fractions import Fraction
    p, s = C.setup(name)
    r = C.read_sys(s / 'sys_result.txt')
    done = C.parse_batch(s, 'sat', C.weta(p))
    first = [int(x, 16) for x in firsts.split(',')]
    lastset = {int(x, 16) for x in last.split(',') if x}
    todo = [(b, k) for b, (k, st, ok) in r.items() if st == 'SAT' and b not in done]
    todo.sort(key=lambda t: (t[0] in lastset, min(bin(t[0] ^ c).count('1') for c in first), t[1], t[0]))
    t0 = time.time()
    stopped = C.run_batch(p, s, 'sat', todo, par, timeout) if todo else 0
    c = C.parse_batch(s, 'sat', C.weta(p))
    print(f"satfirst {name}: SAT betas not yet counted {len(todo)}, finished {sum(1 for b, k in todo if b in c)}, processes stopped at the "
          f"time limit {stopped}, sum {float(sum((c[b]['part'] for b, k in todo if b in c), Fraction(0))):.4f}, seconds {time.time() - t0:.0f}")


def main():
    a = sys.argv
    step, name = a[1], a[2]
    if step == 'satfirst':
        cmd_satfirst(name, int(a[3]), int(a[4]), a[5], a[6] if len(a) > 6 else '')
        return
    if step == 'filter':
        sys.argv = ['paths_filter.py', name, a[3], a[4]]
        FL.main()
    elif step == 'sys':
        sys.argv = ['paths_sys.py', 'run', name, a[3], a[4], a[5], a[6]]
        SY.main()
    elif step == 'satcount':
        RP.cmd_satcount(name, int(a[3]), int(a[4]))
    elif step == 'report':
        RP.cmd_report(name)
    else:
        raise SystemExit('usage: ctr_count.py filter|sys|satcount|report NAME ...')


if __name__ == '__main__':
    main()
