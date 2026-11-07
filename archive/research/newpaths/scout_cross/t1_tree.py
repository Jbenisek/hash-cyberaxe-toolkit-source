"""TEST 1a: in the organizer's reference BLAKE3 (2 rounds), a collision of the LAST CHUNK's compression
(non-root, counter t >= 1, flags CHUNK_START|CHUNK_END = 3, length 55 vs 63) is a full-hash collision.
Method: patch _compress so that the chunk-t compression of B2 returns the CV of B1; then the two full
hashes must agree.  Also log the instance constants (counter, flags, block_len) of that call.
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

import importlib.util, random, struct

path = _hca_public_path_text('__HCA_WORKSPACE__/hash-smash/verifier/blake3.py')
spec = importlib.util.spec_from_file_location("refb3", path)
ref = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ref)
orig = ref._compress
rnd = random.Random(7)


def words_of(block):
    return tuple(struct.unpack("<16I", block.ljust(64, b"\0")))


def run(t, nb_last_extra=0):
    P = bytes(rnd.getrandbits(8) for _ in range(1024 * t))
    pre = bytes(rnd.getrandbits(8) for _ in range(64 * nb_last_extra))  # extra full blocks in last chunk
    B1 = pre + bytes(rnd.getrandbits(8) for _ in range(55))
    B2 = pre + bytes(rnd.getrandbits(8) for _ in range(63))
    w1, w2 = words_of(B1[-55:]), words_of(B2[-63:])
    log = []

    def logging(cv, words, counter, block_len, flags, rounds):
        r = orig(cv, words, counter, block_len, flags, rounds)
        log.append((tuple(words), counter, block_len, flags, tuple(cv) == ref.IV))
        return r
    ref._compress = logging
    h1 = ref.blake3(P + B1, rounds=2)
    calls1 = [c for c in log if c[0] == w1]
    log.clear()
    h2 = ref.blake3(P + B2, rounds=2)
    calls2 = [c for c in log if c[0] == w2]
    # now force the B2 last-block compression to give B1's 8-word CV
    store = {}

    def capture(cv, words, counter, block_len, flags, rounds):
        r = orig(cv, words, counter, block_len, flags, rounds)
        if tuple(words) == w1 and not flags & ref.ROOT:
            store['cv'] = r[:8]
        return r

    def force(cv, words, counter, block_len, flags, rounds):
        r = orig(cv, words, counter, block_len, flags, rounds)
        if tuple(words) == w2 and not flags & ref.ROOT:
            return tuple(store['cv']) + r[8:]
        return r
    ref._compress = capture
    hA = ref.blake3(P + B1, rounds=2)
    ref._compress = force
    hB = ref.blake3(P + B2, rounds=2)
    ref._compress = orig
    return dict(t=t, extra_blocks=nb_last_extra, calls_B1=calls1and(calls1), calls_B2=calls1and(calls2),
                natural_equal=(h1 == h2), forced_equal=(hA == hB), hA_is_h1=(hA == h1))


def calls1and(calls):
    return [(c[1], c[2], c[3], 'cv=IV' if c[4] else 'cv=chained') for c in calls]


if __name__ == "__main__":
    for t, extra in [(1, 0), (2, 0), (3, 0), (5, 0), (1, 1), (3, 2)]:
        print(run(t, extra))
