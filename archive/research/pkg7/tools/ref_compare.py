#!/usr/bin/env python3
"""The experiment program of pkg6 against the reference of the family and its test vectors. Research helper, not submitted.

    python -B tools/ref_compare.py [contexts, default 2000] [members per context, default 25]

Four comparisons (the fourth is described where it is made); the exit status is 0 only if all hold.

  1. Constants and class: the pin, W4', delta, Y3, Y3', Y11, Y11', the class mask and value and every tenth member
     (and the first and last 4,096) against research/h8/design/h8_ref.py.
  2. Context and trial: for random contexts and members, the sixteen words of the program's trial against those of
     h8_ref.context / h8_ref.trial (the generic solver that replays arrangement.txt line by line), the two messages
     against h8_ref.messages, and the state words the program returns against the solver's values.
  3. The test vectors research/h8/gpu/out/ref_vectors.txt (seven context words, Y4, sixteen words, the two digests
     as the organizer's verifier computed them): the program's trial gives the same sixteen words, and its
     compress2 gives the same two digests for the two messages.

Nothing is written.
"""
import importlib.util
import random
import re
import sys
import types
from pathlib import Path

sys.dont_write_bytecode = True
TOOLS = Path(__file__).resolve().parent
PKG = TOOLS.parent
H8 = PKG.parent / "h8"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    contexts = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
    per = int(sys.argv[2]) if len(sys.argv) > 2 else 25
    new = load(PKG / "blake3-r2" / "experiments" / "halfsearch.py", "halfsearch_pkg6")
    ref = load(H8 / "design" / "h8_ref.py", "h8_ref")
    ok = True

    same = ((new.X3, new.X7, new.X11, new.X15, new.W4, new.W13, new.W4B, new.DELTA5, new.ETA, new.LEN_A, new.LEN_B)
            == (ref.X3, ref.X7, ref.X11, ref.X15, ref.W4, ref.W13, ref.W4B, ref.DELTA, ref.ETA, ref.LEN_A, ref.LEN_B)
            and (new.Y3, new.Y3B, new.Y11, new.Y11B) == (ref.Y3A, ref.Y3B, ref.Y11A, ref.Y11B)
            and (new.CLASS_MASK, new.CLASS_VALUE, new.CLASS_FREE, new.CLASS_SIZE)
            == (ref.CLASS_MASK, ref.CLASS_VALUE, ref.CLASS_FREE, ref.CLASS_SIZE)
            and tuple(new.CONTEXT_WORDS) == tuple(ref.CONTEXT_WORDS))
    ks = sorted(set(range(0, new.CLASS_SIZE, 10)) | set(range(4096)) | set(range(new.CLASS_SIZE - 4096, new.CLASS_SIZE)))
    members = sum(new.class_member(k) == ref.class_member(k) and ref.in_class(new.class_member(k)) for k in ks)
    print(f"1. constants, class mask {new.CLASS_MASK:08x}, value {new.CLASS_VALUE:08x}, {new.CLASS_SIZE} members: "
          f"{'equal' if same else 'DIFFERENT'}; members equal {members} of {len(ks)}")
    ok &= same and members == len(ks)

    rng = random.Random(61006)
    total = good = 0
    for n in range(contexts):
        seven = [rng.getrandbits(32) for _ in range(7)]
        if n % 5 == 4:
            seven = [rng.choice((0, new.MASK, v)) for v in seven]
        X, S, w, c0 = new.context(seven)
        ctx = ref.context(dict(zip(new.CONTEXT_WORDS, seven)))
        for _ in range(per):
            k = rng.randrange(new.CLASS_SIZE)
            y4 = new.class_member(k)
            words, (x0, x1, x5, x6, x10, x12, y12) = new.trial(X, S, w, c0, y4)
            rwords, st = ref.trial(ctx, y4)
            state = (all(S[i] == st[f"S{i}"] for i in range(16))
                     and all(X[i] == st[f"X{i}"] for i in (2, 3, 4, 7, 8, 9, 11, 13, 14, 15))
                     and (x0, x1, x5, x6, x10, x12, y12) == tuple(st[n] for n in ("X0", "X1", "X5", "X6", "X10", "X12", "Y12"))
                     and c0 == (st["C0.b1"], st["C0.c1"], st["C0.d1"]))
            total += 1
            good += words == rwords and new.messages(words) == ref.messages(rwords) and state
    print(f"2. context and trial against h8_ref.py: words, messages and state equal in {good} of {total} trials "
          f"({contexts} contexts, every fifth with extreme words)")
    ok &= good == total

    lines = (H8 / "gpu" / "out" / "ref_vectors.txt").read_text().split("\n")
    lines = [line.split() for line in lines if line.strip()]
    good = 0
    for parts in lines:
        v = [int(x, 16) for x in parts]
        seven, y4, words, da, db = v[:7], v[7], v[8:24], v[24:32], v[32:40]
        X, S, w, c0 = new.context(seven)
        mine = new.trial(X, S, w, c0, y4)[0]
        A, B = new.messages(mine)
        good += (len(parts) == 40 and mine == words and new.compress2(A)[1] == da and new.compress2(B)[1] == db
                 and (len(A), len(B)) == (55, 63) and all(da[i] == db[i] for i in (0, 2, 5, 7)))
    print(f"3. test vectors ref_vectors.txt: words of the trial and both digests equal in {good} of {len(lines)} vectors")
    ok &= good == len(lines) and len(lines) > 0

    # 4. the batch with the rule of four conditions against research/h8/batch/h8_batch.py, whose rule that is: the
    # program is read with its line RULE_CONDITIONS set to 4 in memory (no file is touched)
    text = (PKG / "blake3-r2" / "experiments" / "halfsearch.py").read_text(encoding="ascii")
    four_text, count = re.subn(r"^RULE_CONDITIONS = .*$", "RULE_CONDITIONS = 4", text, flags=re.M)
    four = types.ModuleType("halfsearch_rule4")
    exec(compile(four_text, "halfsearch.py with RULE_CONDITIONS = 4", "exec"), four.__dict__)
    h8 = load(H8 / "batch" / "h8_batch.py", "h8_batch")
    total, good = 400, 0
    for n in range(total):
        seven = [rng.getrandbits(32) for _ in range(7)]
        j = four.BATCHES - 1 if n % 8 == 0 else rng.randrange(four.BATCHES)
        X, S, w, c0 = four.context(seven)
        mine = four.packed_batch(four.Machine(), four.batch_constants(X, S, w, c0)[0], j)
        u, v, members = h8.list_words(j)
        theirs = h8.per_member(h8.Machine(), h8.constants(h8.H.context(dict(zip(four.CONTEXT_WORDS, seven)))), u, v, True)
        good += mine == theirs and members == four.list_words(j)[1]
    print(f"4. batch with RULE_CONDITIONS = 4 against h8_batch.py (its rule): stage-2 words, their flags, the final branch, "
          f"the stage-A flags and the stage-A branch equal in {good} of {total} batches (line found {count} time)")
    ok &= good == total and count == 1 and (h8.RULE_ON_H1 == four.RULE_A or sorted(h8.RULE_ON_H1) == sorted(four.RULE_A))
    print("RESULT:", "all equal" if ok else "DIFFERENCES")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
