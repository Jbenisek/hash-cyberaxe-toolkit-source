"""Retarget the copied r7 compact build files to 5 rounds (text substitutions; run once)."""
import re, os, sys
R, U = 5, 1054
H = os.path.dirname(os.path.abspath(__file__))
fm = lambda n: "{:,}".format(n)
pairs = [(45974, 31606), (46231, 31863), (281300, 207120), (1540, 1072), (2747, 2279), (92876, 64108), (185752, 128216), (19, 15)]
reps = [("blake3-r7", "blake3-r5"), ("C(r7)", "C(r5)"), ("blake3(M(x), 7)", "blake3(M(x), 5)"), ("blake3(M, 7)", "blake3(M, 5)"), ("blake3(M,7)", "blake3(M,5)"),
        ("--rounds 7", "--rounds 5"), ("7-round", "5-round"), ("7 rounds, unkeyed", "5 rounds, unkeyed"), ("(7 for the target)", "(5 for the target)"),
        ("#define ROUNDS 7", "#define ROUNDS 5"), ("ROUNDS = 7 ", "ROUNDS = 5 "), ("chained for 7 steps", "chained for 5 steps"), ("7 chained steps", "5 chained steps"),
        ("for _ in range(7):", "for _ in range(5):"), ("1,470", "1,054"), ("1470", "1054"),
        ("B3R7e", "B3R5u5"), ("seven-round", "five-round"), ("seven rounds, the full round count", "five rounds"), ("at seven rounds", "at five rounds"), ("seven rounds", "five rounds"),
        ("BLAKE3, 7 rounds (full BLAKE3)", "BLAKE3, 5 rounds"), ("blake3 round 7", "blake3 round 5"), ("round-7", "round-5")]
for a, b in pairs[:-1]:
    reps += [(fm(a), fm(b)), (str(a), str(b))]
reps += [("used up to 19 times", "used up to 15 times"), ("up to 19 times", "up to 15 times")]
files = ["appA.py", "build_all.py", "embed_gen.py", "org_summary.py", "note_t.md", "proof_t.md", "tm_run.sh", "stage_pre.sh", "stage_run.sh", "cloud_push.sh", "cloud_get.sh",
         "gen_c/build_gen.py", "gen_c/gen_ref.py", "gen_c/make_cport.py", "gen_c/run_gen.py", "gen_c/vm_r7.py", "gen_c/gen.c", "gen_c/native/gen_native.c", "gen_c/native/check.py", "gen_c/native/build_run.sh", "gen_c/native/run2.sh",
         "ext/ex1.py", "ext/exec_records.py", "ext/gen_only.py", "ext/prof.py", "ext/ref_check.py", "ext/ref_regress.py", "cloud_chk/run.sh"] + ["cloud_chk/ext/" + f for f in os.listdir(os.path.join(H, "cloud_chk/ext"))]
for f in files:
    p = os.path.join(H, f)
    t = open(p, encoding="utf-8", newline="").read()
    for a, b in reps:
        t = t.replace(a, b)
    t = t.replace("blake3_r7/compact", "blake3_r5/compact").replace("pos_b3r7e", "pos_b3r5u5").replace("B3R7E", "B3R5U5").replace("b3e", "b3e5")
    open(p, "w", encoding="utf-8", newline="").write(t)
