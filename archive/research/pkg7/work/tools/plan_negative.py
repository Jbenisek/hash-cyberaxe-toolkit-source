#!/usr/bin/env python3
"""Negative test of rule_a_constants(): the program must stop when the plan of rule A (A_PLANS) is wrong.

    python -B work/tools/plan_negative.py          writes work/evidence/plan_negative.txt

The program text is changed in memory, one place at a time (no file is touched), and compiled. Each changed plan
must end in the ValueError of rule_a_constants(). Research helper, not submitted.
"""
import sys
import types

from common import PROGRAM, sha, write

CASES = {
    "wrong mask in the third step": ("(13, 0x40010000)), 0x4F010300)", "(13, 0x40020000)), 0x4F010300)"),
    "wrong distance in the second step": ("(12, 0x0003C000), 12,", "(12, 0x0003C000), 13,"),
    "one read position more": ("0x4F010300)}", "0x4F010301)}"),
    "one read position less": ("0x4F010300)}", "0x4F010200)}"),
    "a shift to the right that brings bits 32 and 33 of the lane to the read positions 8 and 9":
        ("8: (((12, 0x0003C000), 12, (13, 0x40010000)), 0x4F010300)}", "8: (((-24, 0x00000300),), 0x4F010300)}"),
    "a shift to the left that brings a bit of the lane below to a read position":
        ("8: (((12, 0x0003C000), 12, (13, 0x40010000)), 0x4F010300)}", "8: (((30, 0x00000300),), 0x4F010300)}"),
    "the second mask without bit 30 (the eighth condition is not read)":
        ("(13, 0x40010000)), 0x4F010300)", "(13, 0x00010000)), 0x4F010300)"),
}


def main():
    text = PROGRAM.read_text(encoding="ascii")
    out = [f"PROGRAM sha256 {sha()}; python -B work/tools/plan_negative.py"]
    good = True
    exec(compile(text, "unchanged", "exec"), types.ModuleType("unchanged").__dict__)
    out.append("the unchanged program compiles and runs rule_a_constants() without an error")
    for name, (old, new) in CASES.items():
        assert text.count(old) == 1, name
        try:
            exec(compile(text.replace(old, new), "changed", "exec"), types.ModuleType("changed").__dict__)
            out.append(f"NOT STOPPED: {name}")
            good = False
        except ValueError as error:
            out.append(f"stopped: {name}: {error}")
    out.append("RESULT: " + (f"all {len(CASES)} wrong plans are refused" if good else "A WRONG PLAN WAS ACCEPTED"))
    write("plan_negative.txt", out)
    print("\n".join(line[:200] for line in out[1:]))
    return 0 if good else 1


if __name__ == "__main__":
    sys.exit(main())
