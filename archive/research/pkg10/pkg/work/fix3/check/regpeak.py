"""Read-only check: where does the batch reach its register peak under the strict convention (a source stays live
through its instruction)? Imports the package program without changing it (run with python -B)."""

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

orig_at = h.Machine.at
def at(self, part):
    if not hasattr(self, 'marks'):
        self.marks = []
    self.marks.append((self.step, part))
    return orig_at(self, part)
h.Machine.at = at

def profile(m, strict):
    change = [0] * (m.step + 3)
    for v in m.values:
        change[v.born] += 1
        change[v.last + (1 if strict else 0)] -= 1
    held, prof = 0, []
    for d in change:
        held += d
        prof.append(held)
    return prof

def part_of(m, step):
    p = None
    for s, part in m.marks:
        if s <= step:
            p = part
    return p

res = {}
for case in range(40):
    text = "halfsearch selftest %s %d" % ("regcheck", case)
    stream = struct.unpack("<9I", hashlib.shake_256(text.encode("utf-8")).digest(36))
    seven, j = list(stream[:7]), stream[7] % h.BATCHES
    checked, machines = h.batch_check(seven, j)
    m = machines["batch"]
    for strict in (False, True):
        prof = profile(m, strict)
        pk = max(prof)
        parts = sorted(set(part_of(m, s) for s, x in enumerate(prof) if x == pk))
        key = ('strict' if strict else 'program', pk + 2, tuple(parts))
        res[key] = res.get(key, 0) + 1
    assert m.registers() == max(profile(m, False)) + 2
for k, v in sorted(res.items()):
    print(k, v)
