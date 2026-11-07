"""Shared by the tools of research/pkg7/work/tools. Research helper, not submitted.

One program file is worked on: research/pkg7/blake3-r2/experiments/halfsearch.py (16 registers, nine words kept in
registers during a class loop). Every tool writes to work/evidence and names the SHA-256 of the program it ran.
The tools are those of research/pkg7_prep/opt/work/tools, changed for the sub-class, the list V and the rules with
four, six and eight conditions.
"""
import hashlib
import importlib.util
import re
import sys
import types
from pathlib import Path

sys.dont_write_bytecode = True
TOOLS = Path(__file__).resolve().parent
WORK = TOOLS.parent
ROOT = WORK.parent                                  # research/pkg7
TIER = "strict"
PROGRAM = ROOT / "blake3-r2" / "experiments" / "halfsearch.py"
EVIDENCE = WORK / "evidence"
RESEARCH = ROOT.parent
HEAD = ""
RULES = (4, 6, 8)                                   # the rules that the program writes out


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def program():
    return load(PROGRAM, "halfsearch_pkg7")


def program_with(rule=None, **lines):
    """The program with single lines set in memory (no file is touched): RULE_CONDITIONS, and REGISTERS or KEPT."""
    text = PROGRAM.read_text(encoding="ascii")
    if rule is not None:
        lines["RULE_CONDITIONS"] = rule
    for name, value in lines.items():
        text, count = re.subn(rf"^{name} = .*$", f"{name} = {value!r}", text, flags=re.M)
        assert count == 1, name
    module = types.ModuleType("halfsearch_" + "_".join(f"{k}{v}" for k, v in lines.items()))
    exec(compile(text, "halfsearch.py with " + repr(lines), "exec"), module.__dict__)
    return module


def program_with_rule(n):
    return program_with(n)


def rule_text(hs):
    """Rule A of a loaded program as one line: the steps, the read positions and the wanted bits."""
    steps = [("%+d AND %08x" % s) if isinstance(s, tuple) else ("s %+d" % s) for s in hs.A_STEPS]
    return (f"steps {steps}, all {hs.A_ALL:08x}, wanted (position, constant, bits of e1) "
            f"{[(t, w, '%08x' % e) for t, w, e in hs.A_FLIP]}, free bits of e1 read {list(hs.A_FREE)}")


def sha():
    return hashlib.sha256(PROGRAM.read_bytes()).hexdigest()


def write(name, lines):
    text = "\n".join(lines) + "\n"
    EVIDENCE.mkdir(exist_ok=True)
    (EVIDENCE / name).write_bytes(text.encode("ascii"))
    return text
