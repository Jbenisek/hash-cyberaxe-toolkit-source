from pathlib import Path

P = Path(__file__).resolve().parents[2]
p = P / "FILE_STEPS.md"
t = p.read_text(encoding="utf-8")
old = "# pkg7 (DRAFT): state on 2026-10-06 after the step TEXT, how to build it, what is owed before filing\n"
new = old + ("\n**NEWEST STATE: the section \"Step FIX\" at the end (after the three reviews, 23:50). The SHA-256 values just below\n"
             "are those of the step TEXT and are void.**\n")
assert t.count(old) == 1 and "Step FIX (23:50" not in t
t = t.replace(old, new).rstrip("\n") + "\n" + (P / "work" / "fix" / "file_steps_fix_section.md").read_text(encoding="utf-8")
p.write_bytes(t.encode("utf-8"))
print("ok", t.count("\n"), "lines")
