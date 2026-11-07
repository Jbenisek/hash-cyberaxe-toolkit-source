"""One-time editing helper (step PROGRAM of pkg7): the tools copied from research/pkg7_prep/opt/work/tools, changed
for the rules with four, six and eight conditions and the new form of rule A. Every replacement must be found
exactly once (or the stated number of times), or the helper stops. Not submitted."""
from pathlib import Path

T = Path(__file__).resolve().parent


def patch(name, *pairs):
    p = T / name
    t = p.read_text(encoding="ascii")
    for old, new, *count in pairs:
        want = count[0] if count else 1
        if old not in t and new in t:
            continue                                    # already applied
        assert t.count(old) == want, (name, old, t.count(old))
        t = t.replace(old, new)
    p.write_bytes(t.encode("ascii"))
    print("patched", name)


patch("counts.py",
      ("for the rules with 4, 5 and 6 conditions", "for the rules with 4, 6 and 8 conditions"),
      ("from common import HEAD, program_with_rule, sha, write", "from common import HEAD, RULES, program_with_rule, rule_text, sha, write"),
      ("for n in (4, 5, 6):", "for n in RULES:"),
      ("equal to TABLES of the program {equal}; rule A on z: shifts \"\n"
       "                   f\"{[(d, '%08x' % mk) for d, mk in hs.A_SHIFTS]}, add {hs.A_ADD:08x}, all {hs.A_ALL:08x}, value {hs.A_VALUE:08x}\")",
       "equal to TABLES of the program {equal}; rule A on z: \"\n"
       "                   f\"{rule_text(hs)}\")"),
      ("        if n == 5:", "        if n == RULES[-1]:"))
patch("every_use.py",
      ("for n in (4, 5, 6):", "for n in RULES:"),
      ("from common import HEAD, TIER, program_with, sha, write", "from common import HEAD, RULES, TIER, program_with, sha, write"),
      ("assert hs.RESIDENT == () and hs.EVICT == () and not hs.RC_AGAIN and hs.REGISTERS == 16",
       "assert hs.RESIDENT == () and hs.EVICT == () and not hs.RC_AGAIN and not hs.Z_AGAIN and hs.REGISTERS == 16"),
      ("work/evidence_strict/every_use.txt", "work/evidence/every_use.txt", 2))
patch("register_peaks.py",
      ("for n in (4, 5, 6):", "for n in RULES:"),
      ("from common import HEAD, program_with_rule, sha, write", "from common import HEAD, RULES, program_with_rule, sha, write"))
patch("lane_bound.py",
      ("for rule in (4, 5, 6):", "for rule in RULES:"),
      ("from common import HEAD, program_with_rule, sha, write", "from common import HEAD, RULES, program_with_rule, sha, write"),
      ("Per rule (4, 5, 6 conditions, the line RULE_CONDITIONS set in memory)", "Per rule (4, 6, 8 conditions, the line RULE_CONDITIONS set in memory)"),
      ("writes work/evidence_<tier>/lane_bound.txt", "writes work/evidence/lane_bound.txt"),
      ("(detail in work/evidence_*/lane_bound.txt)", "(detail in work/evidence/lane_bound.txt)"),
      ("New in this copy, because the E1 test now has a shift that is not followed by an AND with a rotation mask:",
       "Because the E1 test and the steps of rule A have shifts that are not followed by an AND with a rotation mask:"))
patch("ref_compare.py",
      ("from common import HEAD, RESEARCH, load, program, program_with_rule, sha, write",
       "from common import HEAD, RESEARCH, RULES, load, program, program_with_rule, sha, write"),
      ("""            and (new.CLASS_MASK, new.CLASS_VALUE, new.CLASS_FREE, new.CLASS_SIZE)
            == (ref.CLASS_MASK, ref.CLASS_VALUE, ref.CLASS_FREE, ref.CLASS_SIZE)
""",
       """            and (new.CLASS_MASK, new.CLASS_VALUE) == (ref.CLASS_MASK | new.CUBE[0], ref.CLASS_VALUE | new.CUBE[1])
            and not ref.CLASS_MASK & new.CUBE[0] and new.CLASS_SIZE << bin(new.CUBE[0]).count("1") == ref.CLASS_SIZE
"""),
      ("""    ks = sorted(set(range(0, new.CLASS_SIZE, 10)) | set(range(4096)) | set(range(new.CLASS_SIZE - 4096, new.CLASS_SIZE)))
    members = sum(new.class_member(k) == ref.class_member(k) and ref.in_class(new.class_member(k)) for k in ks)
    out.append(f"1. constants, class mask {new.CLASS_MASK:08x}, value {new.CLASS_VALUE:08x}, {new.CLASS_SIZE} members, the seven "
               f"context words: {'equal' if same else 'DIFFERENT'}; members equal {members} of {len(ks)}")
    ok &= same and members == len(ks)
""",
       """    # the sub-class: exactly the members of the reference class whose e1 = Y3 + Y4 has the bits of CUBE
    inside = [y for y in (ref.class_member(k) for k in range(ref.CLASS_SIZE))
              if (ref.Y3A + y) & new.MASK & new.CUBE[0] == new.CUBE[1]]
    mine = [new.class_member(k) for k in range(new.CLASS_SIZE)]
    members = sum(ref.in_class(y) for y in mine)
    out.append(f"1. constants and the seven context words: {'equal' if same else 'DIFFERENT'}; sub-class mask {new.CLASS_MASK:08x} "
               f"value {new.CLASS_VALUE:08x} = class of h8_ref.py (mask {ref.CLASS_MASK:08x}, {ref.CLASS_SIZE} members) with the "
               f"bits {new.CUBE[0]:08x} of e1 set to {new.CUBE[1]:08x}; members of the program in the class of h8_ref.py: "
               f"{members} of {len(mine)}; the program's members are exactly the {len(inside)} members of that class with "
               f"these bits, in the same order: {mine == inside}")
    ok &= same and members == len(mine) and mine == inside
"""),
      ("""     their flags, the final branch, the seven stage-A flags and the stage-A branch. That program tests its rule on
     z XOR a list word; the program here tests it on z with constants. The counts of the two are printed side by
     side.
""",
       """     their flags and the final branch. tl_batch.py is run on the seven members of the program's list word (it has
     the whole class and the rules of the filed package; its rule with four conditions is the program's rule with
     four conditions), so for the program's rule with four conditions the seven stage-A flags and the stage-A
     branch are compared as well; for six and eight conditions they are not compared here (work/tools/equiv.py and
     the self-test do that). The counts of the two are printed side by side.
"""),
      ("    for rule in (4, 5, 6):\n        hs = program_with_rule(rule)\n", "    for rule in RULES:\n        hs = program_with_rule(rule)\n"),
      ("            ms = tb.members_of(j)\n", "            ms = hs.list_words(j)[1]\n"),
      ("            u, vr = tb.static_words(ms, rule)\n", "            u, vr = tb.static_words(ms, 4)\n"),
      ("            theirs = tb.per_trial(tm, tb.middle_constants(co, octx, zctx), L, vr, rule)\n",
       "            theirs = tb.per_trial(tm, tb.middle_constants(co, octx, zctx), L, vr, 4)\n"
       "            if rule != 4:                       # stage A of tl_batch.py is its rule with four conditions\n"
       "                mine, theirs = mine[:3], theirs[:3]\n"),
      ("            good += (mine == theirs and ms == hs.list_words(j)[1] and u == hs.list_words(j)[0]\n",
       "            good += (mine == theirs and all(ref.in_class(y) for y in ms) and u == hs.list_words(j)[0]\n"),
      ("""        out.append(f"3. rule with {rule} conditions against tl_batch.py: table words, stage-2 words, their flags, the final branch, the "
                   f"stage-A flags and the stage-A branch equal in {good} of {batches} batches; counts here: stage A {one[0][0]}+{one[0][1]}, \"""",
       """        out.append(f"3. rule with {rule} conditions against tl_batch.py: table words, stage-2 words, their flags, the final branch"
                   f"{', the stage-A flags and the stage-A branch' if rule == 4 else ''} "
                   f"equal in {good} of {batches} batches; counts here: stage A {one[0][0]}+{one[0][1]}, \""""),
      ("f\"{one[4][0]}+{one[4][1]}, stage 2 {one[5][0]}+{one[5][1]}, registers {one[6]}, build {one[7][0]}+{one[7][1]}+{one[7][2]}; \"",
       "f\"(its rule 4) {one[4][0]}+{one[4][1]}, stage 2 {one[5][0]}+{one[5][1]}, registers {one[6]}, build {one[7][0]}+{one[7][1]}+{one[7][2]}; \""),
      ("this program is the recoded batch)", "this program is the recoded batch with another rule)"))
patch("check_program.py",
      ('''def rule_on_z(z):
    """The program's condition on z (Lemma A as the program has it), on one 32-bit word."""
    y = z
    for distance, mask in hs.A_SHIFTS:
        y ^= (z >> distance) & mask
    return ((y + hs.A_ADD) & hs.A_ALL) == hs.A_VALUE
''',
       '''def rule_on_z(z, y4):
    """The program's test on z (Lemma A as the program has it), on one 32-bit word, for the member y4: the steps
    A_STEPS, then the XOR with the member's word of the list V, the mask ALL and the comparison with ALL."""
    y, s = z, None
    for step in hs.A_STEPS:
        if isinstance(step, tuple):
            s = ((y << step[0]) if step[0] > 0 else (y >> -step[0])) & step[1]
        else:
            s = (s << step) if step > 0 else (s >> -step)
        y ^= s
    return ((y ^ hs.rule_word(y4)) & hs.A_ALL) == hs.A_ALL
'''),
      ("rule_on_h1(h1, hs.RULE_A) == rule_on_z(z) == hs.rule_a(h1))", "rule_on_h1(h1, hs.RULE_A) == rule_on_z(z, Y[4]) == hs.rule_a(h1))"),
      ("and for each of the three rules the rule on h1 \"\n            f\"and the condition of the program on z say the same",
       "and the rule on h1 \"\n            f\"and the test of the program on z (steps, word of the list V, mask) say the same"),
      ("rule A on h1 equal to the program's condition on z (shifts, addition, mask, value: Lemma A as the\n    program has it)",
       "rule A on h1 equal to the program's test on z (steps, word of the list V, mask: Lemma A as the\n    program has it), Y4 inside the sub-class"))
patch("class_loop.py",
      ("  2. table_build for every one of the 74,899 words of the list,", "  2. table_build for every one of the words of the list (18,725 for the sub-class),"),
      ("  3. middle_step, then packed_batch for ALL 74,899 batches of that value of X2,", "  3. middle_step, then packed_batch for ALL batches of that value of X2,"),
      ("        u, members = hs.list_words(j)\n        static.append(u)\n",
       "        u, members, vw = hs.list_words(j)\n        static.append(u)\n        static_v.append(vw)\n"
       "        v_right += vw == hs.pack(hs.rule_word(y4) for y4 in members)\n"),
      ("    static, shapes, registers, largest, rows_right, seen = [], set(), 0, 0, 0, set()\n",
       "    static, shapes, registers, largest, rows_right, seen = [], set(), 0, 0, 0, set()\n    static_v, v_right = [], 0\n"),
      ("            and len(seen) == hs.CLASS_SIZE and registers <= hs.REGISTERS and largest < 1 << hs.LANE_BITS)\n",
       "            and len(seen) == hs.CLASS_SIZE and registers <= hs.REGISTERS and largest < 1 << hs.LANE_BITS\n"
       "            and v_right == hs.BATCHES and all(x >> 252 == 0 for x in static_v))\n"),
      ("""               f"{len(seen)} different members; per word""",
       """               f"{len(seen)} different members; list V: {v_right} of {hs.BATCHES} words are rule_word() of their seven members; per word"""),
      ("""               f"({len(static) * 32 / 2 ** 20:.2f} MiB); together {(words + len(static)) * 32} bytes "
               f"({(words + len(static)) * 32 / 2 ** 20:.2f} MiB)")""",
       """               f"({len(static) * 32 / 2 ** 20:.2f} MiB); static list V (the same for the whole search, read by stage A of "
               f"every batch) {len(static_v)} words = {len(static_v) * 32} bytes ({len(static_v) * 32 / 2 ** 20:.2f} MiB); together "
               f"{(words + len(static) + len(static_v)) * 32} bytes ({(words + len(static) + len(static_v)) * 32 / 2 ** 20:.2f} MiB)")"""),
      ("outer and the middle loop, the 15 masks of the rotations, the two words of bit 32 and the two bounds of \"",
       "outer and the middle loop, the 15 masks of the rotations, the masks of rule A, the two words of bit 32 and the two bounds of \""))
patch("entry_share.py",
      ("    probe = [0, 1, 6, 7, size - 2, size - 1, 12345, 300000]\n", "    probe = [0, 1, 6, 7, size - 2, size - 1, 12345, size // 2 + 17]\n"),
      ("({batches} per context, the last with two members)", "({batches} per context, the last with {size - full * lanes} members)"),
      ("For each context all 524,288 members of the class are tried in the order of the program's list:\n"
       "seven consecutive members are one batch, and the last batch holds the last two members (its five spare lanes\n"
       "repeat the last member and add no trial).",
       "For each context all members of the sub-class (131,072) are tried in the order of the program's list:\n"
       "seven consecutive members are one batch, and the last batch holds the last four members (its three spare lanes\n"
       "repeat the last member and add no trial)."),
      ("For each of the three rules of the program (four, five and six conditions on h1)", "For each of the three rules of the program (four, six and eight conditions on h1)"))
patch("selftest_small.py",
      ('r["members_in_list"] == 2 ** 19,', 'r["members_in_list"] == 2 ** 17 == r["class"]["members"]\n'
       '             and (r["class"]["mask"], r["class"]["value"]) == ("07ef8303", "030c0303"),'),
      ("""f"flags right on all 128 patterns of zero lanes and on all {r['rule_a_patterns']} words of rule A patterns")""",
       """f"flags right on all 128 patterns of zero lanes and on all {r['rule_a_patterns']} words of rule A patterns (every "
             f"pattern of the bits of z that the rule reads with every pattern of the free bits {r['rule_a_on_z']['free_bits_of_e1']} "
             f"of e1, once in every lane; in {r['rule_a_patterns_satisfied']} words a lane satisfies the rule)")"""))
