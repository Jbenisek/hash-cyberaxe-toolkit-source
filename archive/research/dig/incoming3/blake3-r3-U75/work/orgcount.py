# Organizer reference op count of blake3 _compress at 1,2,3,7 rounds by operation type (their Word-counter method, run on THEIR verifier only).

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

import sys, operator, collections
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/pareto_clone'))
from verifier import blake3
tally=collections.Counter()
class Word(int): pass
def mk(name,op):
    def f(self,other=None):
        tally[name]+=1
        return Word(op(int(self)) if other is None else op(int(self),int(other)))
    return f
for n,o in {"add":operator.add,"and":operator.and_,"or":operator.or_,"xor":operator.xor,"lshift":operator.lshift,"rshift":operator.rshift}.items():
    setattr(Word,f"__{n}__",mk(n,o))
for r in (1,2,3,7):
    tally.clear()
    blake3._compress(tuple(Word(x) for x in blake3.IV),tuple(Word(i) for i in range(16)),Word(0),Word(64),Word(11),r)
    print('rounds',r,'total',sum(tally.values()),dict(tally))
