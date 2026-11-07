"""One-time helper (step PROGRAM of pkg7): the scripts that came with the copy of research/pkg6 and still name
research/pkg6 by its absolute path would, if run from here, write into the FILED package. Each gets a first
statement that stops it. The step that ports the text removes the guard when it has set the paths. Not submitted."""
from pathlib import Path

PKG = Path(__file__).resolve().parent.parent.parent
MESSAGE = ("STOP: copy of a script of research/pkg6 inside research/pkg7; it still points at research/pkg6, which is "
           "filed and read only. Not ported yet (PROGRAM_STEP.md, section 6 item 1).")
SHELL = ["validate_pkg6.sh", "tools/rule_a_sat2_all.sh", "tools/rule_a_sat2_one.sh", "tools/rule_a_sat_all.sh",
         "tools/rule_drat_all.sh", "tools/selftest_big.sh", "tools/selftest_big_launch.sh"]
for name in SHELL:
    p = PKG / name
    lines = p.read_bytes().decode("utf-8").split("\n")
    assert lines[0].startswith("#!"), name
    if "STOP: copy of a script" not in lines[1]:
        lines.insert(1, f'echo "{MESSAGE}"; exit 9')
        p.write_bytes("\n".join(lines).encode("utf-8"))
    print("guarded", name)
p = PKG / "ready_all.ps1"
text = p.read_bytes().decode("utf-8")
if "STOP: copy of a script" not in text:
    newline = "\r\n" if "\r\n" in text else "\n"
    p.write_bytes((f'Write-Output "{MESSAGE}"; exit 9{newline}' + text).encode("utf-8"))
print("guarded ready_all.ps1")
