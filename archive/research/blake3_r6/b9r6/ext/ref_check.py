"""External check (not shipped): the program's scalar digest vs the organizer reference verifier/blake3.py at 3 rounds first, then 4 (target) and 7, and at 7 rounds
both vs the blake3 library (pip blake3 1.0.11).   usage: ref_check.py <organizer-repo-dir> <experiments-dir>"""
import sys, random, struct, importlib.util
sys.dont_write_bytecode = True
V, X = sys.argv[1], sys.argv[2]
spec = importlib.util.spec_from_file_location("ref_blake3", V + "/verifier/blake3.py"); ref = importlib.util.module_from_spec(spec); spec.loader.exec_module(ref)
sys.path.insert(0, X); import bsrho as b
rnd = random.Random(20261015)
def mine(msg, rounds):
    w = list(struct.unpack("<16I", msg)); d = b.digest_words(w, rounds)
    return struct.pack("<8I", *d)
for rounds in (3, 4, 6):
    bad = 0; n = 2000
    for _ in range(n):
        x = rnd.getrandbits(256); msg = b.message(x) if _ % 2 == 0 else rnd.randbytes(64)
        bad += mine(msg, rounds) != ref.blake3(msg, rounds)
    print("rounds %d: program digest_words vs organizer blake3(M, %d) on %d 64-byte messages (half of the form 0^32 || x): %d differences" % (rounds, rounds, n, bad))
try:
    sys.path.insert(0, sys.argv[3]); import blake3 as lib
    bad = 0; n = 2000; bad2 = 0
    for i in range(n):
        msg = rnd.randbytes(64)
        bad += mine(msg, 7) != lib.blake3(msg).digest()
        bad2 += ref.blake3(msg, 7) != lib.blake3(msg).digest()
    ln = [0, 1, 63, 64, 65, 1023, 1024, 1025, 2048, 3000]
    bad3 = sum(ref.blake3(m, 7) != lib.blake3(m).digest() for m in (rnd.randbytes(k) for k in ln))
    print("7 rounds (full BLAKE3): program digest_words vs blake3 library on %d messages: %d differences; organizer verifier vs library: %d differences on the same, %d on lengths %s" % (n, bad, bad2, bad3, ln))
except ImportError as e:
    print("blake3 library not available:", e)
