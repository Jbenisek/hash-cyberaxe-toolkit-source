"""Read-only: under the strict convention, which steps of a batch hold 15 values (17 registers), in which parts, and is
there a kept (resident) word that is not used anywhere between the first and the last such step (so that dropping it
and loading it once again costs one load per batch)? Run with python -B."""

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

import sys, struct, hashlib
sys.dont_write_bytecode = True
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/pkg7/blake3-r2/experiments'))
import halfsearch as h

orig_at, orig_value = h.Machine.at, h.Machine.value
USES = {}
def at(self, part):
    if not hasattr(self, 'marks'):
        self.marks = []
    self.marks.append((self.step, part))
    return orig_at(self, part)
def value(self, z, *used):
    r = orig_value(self, z, *used)
    for u in used:
        USES.setdefault(id(u), []).append(self.step)
    return r
h.Machine.at, h.Machine.value = at, value

def part_of(m, step):
    p = None
    for s, part in m.marks:
        if s <= step:
            p = part
    return p

summary = {}
for case in range(40):
    text = "halfsearch selftest %s %d" % ("spillcheck", case)
    stream = struct.unpack("<9I", hashlib.shake_256(text.encode("utf-8")).digest(36))
    seven, j = list(stream[:7]), stream[7] % h.BATCHES
    USES.clear()
    checked, machines = h.batch_check(seven, j)
    m = machines["batch"]
    change = [0] * (m.step + 3)
    for v in m.values:
        change[v.born] += 1
        change[v.last + 1] -= 1
    held, prof = 0, []
    for d in change:
        held += d
        prof.append(held)
    pk = max(prof)
    peaks = [s for s, x in enumerate(prof) if x == pk]
    parts = [part_of(m, s) for s in peaks]
    # resident/kept words: values born in the resident() call (no 'at' yet) or get()
    first_part_step = m.marks[0][0] if m.marks else 0
    kept = [v for v in m.values if v.born <= first_part_step]
    lo, hi = min(peaks), max(peaks)
    free = [v for v in kept if v.born < lo and v.last > hi and not any(lo <= u <= hi for u in USES.get(id(v), []))]
    # stage-A-only peaks (stage 2 parts are not run by every batch)
    stage_a = [s for s, p in zip(peaks, parts) if p in ('loop', 'X0 to X10', 'C2 to z', 'rule A')]
    key = (pk + 2, tuple(sorted(set(parts))), len(peaks), len(kept), len(free))
    if stage_a:
        la, ha = min(stage_a), max(stage_a)
        free_a = [v for v in kept if v.born < la and v.last > ha and not any(la <= u <= ha for u in USES.get(id(v), []))]
        key += ('stageA peaks', len(stage_a), 'kept free across them', len(free_a))
        any_a = [v for v in m.values if v.born < la and v.last > ha and not any(la <= u <= ha for u in USES.get(id(v), []))]
        # greedy: fewest words whose release covers every stage-A peak step (each word covers the peak steps inside
        # one gap between its uses); report whether one word covers all, else how many a greedy cover takes
        gaps = []
        for v in m.values:
            us = sorted(set([v.born] + USES.get(id(v), []) + [v.last]))
            for a, b in zip(us, us[1:]):
                cov = frozenset(s for s in stage_a if a < s < b)
                if cov:
                    gaps.append(cov)
        left, n = set(stage_a), 0
        while left and n < 9:
            best = max(gaps, key=lambda g: len(g & left))
            if not best & left:
                n = 99; break
            left -= best; n += 1
        key += ('any value free across all', len(any_a), 'greedy words to cover', n)
    summary[key] = summary.get(key, 0) + 1
for k, v in summary.items():
    print(k, v)
print('parts in order:', [p for s, p in machines["batch"].marks])
