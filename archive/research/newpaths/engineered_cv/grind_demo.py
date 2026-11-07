r"""Engineered chaining value: end-to-end demo at reduced size, and the one-formula score (research only).
Part 1: grind 64-byte first blocks (flags CHUNK_START, counter 0) until the top 16 bits of CV word J take a chosen
value (2^16 expected; a full word is 2^32, out of reach in pure Python in a short run), then build the free-half
block on that CV (pin H8, 55/63, flags 10) and check the organizer digest of the complete 119/127-byte messages.
Part 2: score = log2(2^T + 2^(32 k)) with T from the one formula (counter\adjudicate\adj_check.py, as CENSUS.md).
usage: python -B grind_demo.py J SEED
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

import sys, struct, random, time, math
sys.dont_write_bytecode = True
HERE = _hca_public_path_text('__HCA_WORKSPACE__/research/newpaths/engineered_cv')
sys.path.insert(0, HERE)
sys.path.insert(1, _hca_public_path_text('__HCA_WORKSPACE__/hash-smash/verifier'))
import blake3 as V
import construct as C

M = 0xFFFFFFFF
H8 = (0x29D4FA98, 0xBEE3AF28, 0x44036000, 0x40C58500, 0x97475638, 0x0007C006)
HALF = (0, 2, 5, 7)


def one_formula(Cr, m, ops, pen=0.0):
    return math.log2(0.5) + 128 - math.log2(Cr / m) + math.log2(ops / 430) + 0.02 + pen


def main():
    J = int(sys.argv[1]); rng = random.Random(int(sys.argv[2]))
    target = 0x0000
    t0 = time.time(); tries = 0
    while True:
        tries += 1
        pre = bytes(rng.getrandbits(8) for _ in range(64))
        cv = tuple(V._compress(V.IV, struct.unpack('<16I', pre), 0, 64, 1, 2)[:8])
        if cv[J] >> 16 == target:
            break
    print(f'grind: CV word {J} top 16 bits = {target:04x} after {tries} first blocks ({time.time() - t0:.0f}s); cv[{J}] = {cv[J]:08x}')
    ok = 0; n = 3
    for _ in range(n):
        P = C.transfer(H8, cv, 55, 63)
        o = C.outer(P, cv, 55, 10, 0, *[rng.getrandbits(32) for _ in range(8)])
        wa, wb = C.inner_const(P, o, cv, 0)
        A, okA = C.block_bytes(wa, 55); B, okB = C.block_bytes(wb, 63)
        dA = struct.unpack('<8I', V.blake3(pre + A, 2)); dB = struct.unpack('<8I', V.blake3(pre + B, 2))
        ok += okA and okB and all(dA[i] == dB[i] for i in HALF) and dA != dB
    print(f'complete messages {64 + 55}/{64 + 63} bytes on the ground CV: organizer digest words 0,2,5,7 equal, '
          f'messages and digests distinct {ok}/{n}')
    Cr, ops = 185377197.55, 7.7              # H8 sub-class C15 and H8's counted machine (CENSUS.md section 1)
    for m in (2.0, 1.4):
        T = one_formula(Cr, m, ops)
        row = ' '.join(f'k={k}: {math.log2(2 ** T + 2 ** (32 * k)):.2f}' for k in (0, 1, 2, 3))
        print(f'score, margin {m}: rate change 0 per chosen word -> {row}')


if __name__ == '__main__':
    main()
