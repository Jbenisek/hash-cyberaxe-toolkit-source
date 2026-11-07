"""Check every pair returned by the Orchard runs with the organizer's digest (verifier/poseidon.py of the staged clone, r = 23):
messages (A, rho) and (B, rho) as two 32-byte little-endian encodings, A != B, low w bits of the two digests equal.
Usage (WSL): python3 -B verify_pairs.py /root/hashsmash/yukon/pos_posgen3"""
import sys, os, glob, json
sys.path.insert(0, sys.argv[1])
sys.dont_write_bytecode = True
from verifier.poseidon import digest  # organizer code

HERE = os.path.dirname(os.path.abspath(__file__))
tot = ok = 0
byw = {}
for f in sorted(glob.glob(os.path.join(HERE, "data", "*", "orch*.jsonl"))):
    for line in open(f):
        d = json.loads(line)
        if d["status"] != "found":
            continue
        tot += 1
        rho = d["fn"].to_bytes(32, "little")
        a, b = d["A"].to_bytes(32, "little") + rho, d["B"].to_bytes(32, "little") + rho
        da, db = int.from_bytes(digest(a, 23), "little"), int.from_bytes(digest(b, 23), "little")
        m = (1 << d["w"]) - 1
        good = a != b and (da & m) == (db & m) and da != db
        ok += good
        byw.setdefault(d["w"], [0, 0]); byw[d["w"]][0] += 1; byw[d["w"]][1] += good
out = json.dumps({"pairs": tot, "verified_by_organizer_digest": ok, "by_width": byw})
open(os.path.join(HERE, "data", "pairs.json"), "w").write(out)
print(out)
