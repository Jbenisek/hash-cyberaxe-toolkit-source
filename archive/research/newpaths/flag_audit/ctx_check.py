# Context check on the organizer verifier (read-only import, no file writes).
# Logs every compression call: role, cv origin, counter (v12,v13), block_len (v14), flags (v15).

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

import importlib.util, sys

P = _hca_public_path_text('__HCA_WORKSPACE__/hash-smash/verifier/blake3.py')
spec = importlib.util.spec_from_file_location("orgb3", P)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

orig = m._compress
log = []
outs = {}


def tag(cv):
    if tuple(cv) == tuple(m.IV):
        return "IV"
    return outs.get(tuple(cv), "?")


def wrapped(cv, words, counter, block_len, flags, rounds):
    out = orig(cv, words, counter, block_len, flags, rounds)
    rec = dict(cv=tag(cv), v12=counter & m.MASK, v13=counter >> 32,
               v14=block_len, v15=flags, words=tuple(words), out=tuple(out[:8]))
    log.append(rec)
    outs[tuple(out[:8])] = "chain#%d" % (len(log) - 1)
    return out


m._compress = wrapped


def run(data, label):
    log.clear(); outs.clear()
    h = m.blake3(data, 2)
    print("== %s (len %d, chunks %d)" % (label, len(data), max(1, (len(data) + 1023) // 1024)))
    for i, r in enumerate(log):
        print("  #%-3d cv=%-9s v12=%-4d v13=%d v14=%-2d v15=%-2d" % (i, r["cv"], r["v12"], r["v13"], r["v14"], r["v15"]))
    return h, list(log)


def compact(data, label):
    # Print only distinct (cv-kind, v12, v13, v14, v15) contexts, and the root call.
    log.clear(); outs.clear()
    m.blake3(data, 2)
    seen = []
    for r in log:
        k = ("IV" if r["cv"] == "IV" else "chain", r["v12"], r["v13"], r["v14"], r["v15"])
        if k not in seen:
            seen.append(k)
    print("== %s (len %d): distinct contexts %s" % (label, len(data), seen))
    return list(log)


b = bytes(range(256)) * 20
run(b"", "empty")
run(b[:1], "1 byte")
run(b[:64], "64 bytes")
run(b[:65], "65 bytes")
compact(b[:1024], "1024 bytes")
compact(b[:1025], "1025 bytes (last chunk 1 byte)")
compact(b[:2048 + 64], "3 chunks, last chunk 64 bytes")
compact(b[:3 * 1024 + 700], "4 chunks, last chunk 700 bytes")

# Leaf-vs-parent alignment: A = 3 chunks (last chunk t=2 single block), B = 4 full chunks, shared chunks 0,1.
X = b[:2048]
A = X + b"\x11" * 50
B = X + b"\x22" * 2048
la = compact(A, "A")
lb = compact(B, "B")
ra, rb = la[-1], lb[-1]
print("A root: cv=%s v14=%d v15=%d ; B root: cv=%s v14=%d v15=%d" % (ra["cv"], ra["v14"], ra["v15"], rb["cv"], rb["v14"], rb["v15"]))
print("root left halves equal:", ra["words"][:8] == rb["words"][:8])
leafA = [r for r in la if r["v12"] == 2][-1]
parB = [r for r in lb if r["v15"] == 4 and r["words"][:8] != ra["words"][:8]][-1]
print("A root right half == A chunk-2 CV (v12=2,v14=%d,v15=%d):" % (leafA["v14"], leafA["v15"]), ra["words"][8:] == leafA["out"])
print("B root right half == B parent(2,3) CV (v12=%d,v14=%d,v15=%d):" % (parB["v12"], parB["v14"], parB["v15"]), rb["words"][8:] == parB["out"])
print("=> roots identical iff CV_leaf(A,t=2) == CV_parent(B,P23): inputs equal otherwise:",
      (ra["cv"], ra["v12"], ra["v13"], ra["v14"], ra["v15"]) == (rb["cv"], rb["v12"], rb["v13"], rb["v14"], rb["v15"]))

# Counter range under the domain: len < 2^61 bytes.
tmax = (((1 << 61) - 1) + 1023) // 1024 - 1
print("max chunk index", tmax, "= 2^51-1:", tmax == (1 << 51) - 1, " v13 max", tmax >> 32, "= 2^19-1:", (tmax >> 32) == (1 << 19) - 1)

# Counter only touches the chunk's own compressions: same last chunk at t=1 vs t=2 gives different CV;
# chunk output descriptor carries counter=t into every block of that chunk.
d1 = m._chunk_output(b"\x33" * 200, 1, 2)
d2 = m._chunk_output(b"\x33" * 200, 2, 2)
print("multi-block chunk: chained cv into last block depends on t:", d1[0] != d2[0], " last-block (v12,v14,v15):", d1[2], d1[3], d1[4])
s1 = m._chunk_output(b"\x33" * 40, 7, 2)
print("single-block chunk at t=7: cv is IV:", tuple(s1[0]) == tuple(m.IV), " (v12,v14,v15):", s1[2], s1[3], s1[4])

# START bit <=> cv is IV, over every leaf call seen in a few messages.
ok = True
for L in (0, 1, 64, 65, 1024, 1025, 2112, 3772, 5000):
    log.clear(); outs.clear(); m.blake3(b[:L] if L <= len(b) else (b * 3)[:L], 2)
    for r in log:
        if r["v15"] & 4:
            ok &= r["cv"] == "IV"
        else:
            ok &= ((r["v15"] & 1) == 1) == (r["cv"] == "IV")
print("leaf: START bit set <=> cv is IV; parent: cv is IV  (all calls, 9 lengths):", ok)

# Block-shift pair: A = a0||rest, B = b0||b1||rest, same chunk index.  If CV after A block 0 equals CV after
# B block 1, every later call has identical (v12,v13,v14,v15): check the parameter sequences align.
rest = b[300:300 + 3 * 64 + 20]
for pre, lab in ((b"", "root chunk"), (b[:1024], "final chunk t=1")):
    log.clear(); outs.clear(); m.blake3(pre + b"\xaa" * 64 + rest, 2); la2 = list(log)
    log.clear(); outs.clear(); m.blake3(pre + b"\xbb" * 128 + rest, 2); lb2 = list(log)
    k = len(pre) // 1024 * 16  # skip chunk-0 calls (16 blocks; no parent is formed before the final chunk)
    pa = [(r["v12"], r["v13"], r["v14"], r["v15"]) for r in la2[k:]]
    pb = [(r["v12"], r["v13"], r["v14"], r["v15"]) for r in lb2[k:]]
    print("block-shift (%s): A deciding call %s vs B deciding call %s; later params equal: %s" %
          (lab, pa[0], pb[1], pa[1:] == pb[2:]))
