#!/usr/bin/env python3
"""One complete outer step as the algorithm runs it: the whole table once, then the batches of several values of X2.

    python -B work/tools/class_loop.py [more values of X2, default 3] [batches for each of them, default 3000]

writes work/evidence/class_loop.txt. Research helper, not submitted. It uses the program's own counted pieces:

  1. outer_step once, on one machine (one context drawn here);
  2. table_build for every one of the words of the list (18,725 for the sub-class), each on a new machine: the five lists of the table
     are allocated here in full (the program itself builds only the words of the batch it counts) and compared
     with table_row() of every member; the counts of all words are added up;
  3. middle_step, then packed_batch for ALL batches of that value of X2, each with the words of the table
     built in step 2, every lane checked as the program's batch_check checks it (against the complete digests of
     the lane's two real messages);
  4. middle_step again, several times in a row on the same memory, so that X2 goes up by one each time, and for
     each new value the given number of batches drawn at random, with the SAME table: this is the point of the
     arrangement, the table of an outer step serves every value of X2.

It then states the memory: the number of words of the table and of the static list as allocated here, their size
as 256-bit words, and the number of memory cells the pieces use.
"""
import random
import sys
import time

from common import HEAD, program, sha, write


def main():
    more = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    sample = int(sys.argv[2]) if len(sys.argv) > 2 else 3000
    hs = program()
    rng = random.Random(20261006)
    seven = [rng.getrandbits(32) for _ in range(7)]
    out = [f"{HEAD}PROGRAM sha256 {sha()}; python -B work/tools/class_loop.py {more} {sample}; rule with {len(hs.RULE_A)} conditions; "
           f"context {' '.join('%08x' % x for x in seven)}"]
    ok = True
    start = time.time()
    c = hs.memory(seven)
    fixed_cells = len(c) - 7
    mo = hs.Machine()
    hs.outer_step(mo, c)
    o = hs.outer(seven[:6])
    names = ("XA", "X6", "X1", "R", "Y12")
    table = {name: [] for name in names}
    static, shapes, registers, largest, rows_right, seen = [], set(), 0, 0, 0, set()
    static_v, v_right = [], 0
    static_v, v_right = [], 0
    static_v, v_right = [], 0
    total = [0, 0, 0]
    for j in range(hs.BATCHES):
        m = hs.Machine()
        row = hs.table_build(m, c, j)
        u, members, vw = hs.list_words(j)
        static.append(u)
        static_v.append(vw)
        v_right += vw == hs.pack(hs.rule_word(y4) for y4 in members)
        seen.update(members)
        for name in names:
            table[name].append(row[name])
        want = [hs.table_row(o, y4) for y4 in members]
        rows_right += row == {name: hs.pack(r[name] for r in want) for name in names}
        shapes.add(tuple((p, m.ops[p], m.loads[p], m.stores[p]) for p in m.ops))
        registers = max(registers, m.registers())
        largest = max(largest, max(m.sums.values()))
        for i, kind in enumerate((m.ops, m.loads, m.stores)):
            total[i] += sum(kind.values())
    one = sorted(shapes)[0]
    per_word = tuple(sum(r[i] for r in one) for i in (1, 2, 3))
    good = (rows_right == hs.BATCHES and len(shapes) == 1 and one == tuple(r[:4] for r in hs.TABLES["table build"])
            and len(seen) == hs.CLASS_SIZE and registers <= hs.REGISTERS and largest < 1 << hs.LANE_BITS
            and v_right == hs.BATCHES and all(x >> 252 == 0 for x in static_v))
    ok &= good
    out.append(f"1.-2. outer step once; table: {hs.BATCHES} words built, {rows_right} equal to table_row() of their seven members, "
               f"{len(seen)} different members; list V: {v_right} of {hs.BATCHES} words are rule_word() of their seven members; per word {per_word[0]} operations + {per_word[1]} loads + {per_word[2]} stores = "
               f"{sum(per_word)} in every word ({len(shapes)} shape); whole table {total[0]} + {total[1]} + {total[2]} = {sum(total)} "
               f"(2^{__import__('math').log2(sum(total)):.2f}); registers {registers}; largest lane {largest.bit_length()} bits; "
               f"{'ok' if good else 'FAIL'} ({time.time() - start:.0f} s)")
    entered = 0
    for step in range(1 + more):
        start = time.time()
        mm = hs.Machine()
        hs.middle_step(mm, c)
        x2 = (seven[6] + step) & hs.MASK
        v = hs.context(seven[:6] + [x2])
        by_outer, by_middle = hs.stored(v)
        cells = all(c[name] == hs.rep(value) for group in (by_outer, by_middle) for name, value in group.items())
        js = range(hs.BATCHES) if step == 0 else sorted(rng.sample(range(hs.BATCHES), sample - 1) + [hs.BATCHES - 1])
        right = lanes = passing_all = entered_here = zero_all = 0
        shapes, registers, largest = set(), 0, 0
        for j in js:
            m = hs.Machine()
            words, flags, taken, flags_a, taken_a = hs.packed_batch(m, c, {name: table[name][j] for name in names}, j, entered)
            members = hs.list_words(j)[1]
            refs = [hs.reference(v, y4) for y4 in members]
            passing = [int(hs.rule_a(r["h1"])) for r in refs]
            good_lanes = sum(int(r["words"] == 1 and r["y4"] == members[i] and r["half"] == 1 and flags_a[i] == 1 - passing[i]
                                 and words[i] == r["word"] and r["word"] == r["word_from_digests"]
                                 and flags[i] == int(r["word"] != 0)) for i, r in enumerate(refs))
            zero = sum(int(r["word"] == 0) for r in refs)
            if taken_a != (1 in passing) or taken != (zero > 0):
                good_lanes = 0
            right += good_lanes
            lanes += hs.LANES
            passing_all += sum(passing)
            entered_here += int(taken_a)
            zero_all += zero
            parts = list(m.ops)
            a, s2 = parts[:hs.STAGE_A_PARTS], parts[hs.STAGE_A_PARTS:]
            shapes.add((sum(m.ops[p] for p in a), sum(m.loads[p] for p in a), sum(m.ops[p] for p in s2), sum(m.loads[p] for p in s2)))
            registers = max(registers, m.registers())
            largest = max(largest, max(m.sums.values()))
        entered += entered_here
        good = cells and right == lanes and len(shapes) == 1 and registers <= hs.REGISTERS and largest < 1 << hs.LANE_BITS
        ok &= good
        out.append(f"{'3.' if step == 0 else '4.'} X2 = {x2:08x} (middle step number {step + 1} on the same memory, stored words right: "
                   f"{cells}): {len(js)} batches {'(all)' if step == 0 else '(drawn, with the last)'} with the table of step 2, "
                   f"{right} of {lanes} lanes right, stage counts {sorted(shapes)}, registers {registers}, largest lane "
                   f"{largest.bit_length()} bits; lanes that satisfy rule A {passing_all}, batches that enter stage 2 {entered_here} "
                   f"({entered_here / len(js):.4f}), zero stage-2 words {zero_all}; {'ok' if good else 'FAIL'} ({time.time() - start:.0f} s)")
    # memory
    words = sum(len(table[name]) for name in names)
    py = sum(sys.getsizeof(x) for name in names for x in table[name]) + sum(sys.getsizeof(table[name]) for name in names)
    py_static = sum(sys.getsizeof(x) for x in static) + sys.getsizeof(static)
    by_outer, by_middle = hs.stored(hs.context(seven))
    out.append(f"memory, as allocated here with the program's table_build and list_words: table of an outer step {len(names)} lists * "
               f"{hs.BATCHES} words = {words} words of 256 bits = {words * 32} bytes ({words * 32 / 2 ** 20:.2f} MiB); static list "
               f"U (the same for the whole search, read only by the table build) {len(static)} words = {len(static) * 32} bytes "
               f"({len(static) * 32 / 2 ** 20:.2f} MiB); static list V (the same for the whole search, read by stage A of "
               f"every batch) {len(static_v)} words = {len(static_v) * 32} bytes ({len(static_v) * 32 / 2 ** 20:.2f} MiB); together "
               f"{(words + len(static) + len(static_v)) * 32} bytes ({(words + len(static) + len(static_v)) * 32 / 2 ** 20:.2f} MiB)")
    out.append(f"   a word holds seven lanes of {hs.LANE_BITS} bits (252 of 256 bits), 32 payload bits per lane; the last word of every "
               f"list has {hs.LANES * hs.BATCHES - hs.CLASS_SIZE} spare lanes that repeat the last member; payload "
               f"{len(names)} * {hs.CLASS_SIZE} * 4 = {len(names) * hs.CLASS_SIZE * 4} bytes")
    out.append(f"   memory cells (one 256-bit word each): {len(by_outer)} stored by the outer step, {len(by_middle)} stored by the "
               f"middle step, 7 for the words of the context, {fixed_cells} fixed (among them the two end-test cells of the "
               f"outer and the middle loop, the 15 masks of the rotations, the masks of rule A, the two words of bit 32 and the two bounds of "
               f"the batch loop); registers of the batch machine: {hs.REGISTERS}, of them {len(hs.RESIDENT)} hold kept words")
    out.append(f"   as CPython objects in this tool (information only): table {py} bytes, static list {py_static} bytes; the "
               f"program itself never holds more than the five words of one batch")
    out.append("RESULT: " + ("all steps hold" if ok else "FAILED"))
    write("class_loop.txt", out)
    for line in out[1:]:
        print(line[:330])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
