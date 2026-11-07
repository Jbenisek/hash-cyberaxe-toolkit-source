"""Export gdx models for target sets (E1/E3 internal words prescribed on top of the pinned family)."""
import subprocess
import sys

SETS = {
    "base": [],
    "y4": ["Y4"],
    "y4_g1": ["Y4", "E3.c1"],
    "y4_h1": ["Y4", "E3.d1"],
    "y4_e2": ["Y4", "E3.a2"],
    "y4_e1d1": ["Y4", "E1.d1"],
    "y4_e1a2": ["Y4", "E1.a2"],
    "y4_e1a1": ["Y4", "E1.a1"],
    "y4_g2": ["Y4", "E3.c2"],
    "g1": ["E3.c1"],
    "e1d1": ["E1.d1"],
    "h1": ["E3.d1"],
    "y4_g1_e1d1": ["Y4", "E3.c1", "E1.d1"],
    "y4_h1_g1": ["Y4", "E3.d1", "E3.c1"],
    "y4_h1_e1d1": ["Y4", "E3.d1", "E1.d1"],
    "y4_w5_e1d1": ["Y4", "w5", "E1.d1"],
    "y4_w5_g1": ["Y4", "w5", "E3.c1"],
}

SETS["y4_w5"] = ["Y4", "w5"]          # positive control: the published basis contains both

if __name__ == "__main__":
    tabs = 0
    args = sys.argv[1:]
    if args and args[0] == "--t2":
        tabs = 1
        args = args[1:]
    names = args or list(SETS)
    for nm in names:
        suffix = "_t2" if tabs else ""
        out = subprocess.run([sys.executable, "-B", "pin_model.py", "export", ",".join(SETS[nm]),
                              f"m_{nm}{suffix}.model", str(tabs)], capture_output=True, text=True)
        print(nm + suffix, len(SETS[nm]), (out.stdout.strip().splitlines() or [out.stderr])[-1])
