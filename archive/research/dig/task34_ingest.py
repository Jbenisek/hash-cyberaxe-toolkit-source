import json
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parent
source = root / "TASK34_R40_CELLS_INPUT.jsonl"
adder = root / "add_cell.py"
for line_no, line in enumerate(source.read_text(encoding="utf-8").splitlines(), 1):
    rec = json.loads(line)
    result = subprocess.run([sys.executable, str(adder), "--json", json.dumps(rec, separators=(",", ":"))], text=True)
    if result.returncode:
        raise SystemExit(f"add_cell failed at line {line_no}: {rec['id']}")
print(f"added {line_no} Task34 cells")
