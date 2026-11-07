#!/usr/bin/env python3
"""Freeze the night's files that are still growing, so that the text does not move with them. Research helper.

Some result files of research/night/main are logs of jobs that were still running when the package was written
(the solver search, the search for classes with the constants fixed, the tables made from them). The text quotes
counts from them ("the log holds N sets of constants"). This tool copies them to evidence/snapshot/;
tools/pkg5_data.py reads a file from there when it is there, and from research/night/main otherwise. Run it again
to take the files as they are now, then rebuild and validate.

    python -B tools/snapshot_logs.py           copy the files and say which copies changed
    python -B tools/snapshot_logs.py --check   say which copies differ from the night's files; copy nothing
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pkg5_data as data  # noqa: E402


def main():
    check = "--check" in sys.argv
    target = data.EVID / "snapshot"
    if not check:
        target.mkdir(parents=True, exist_ok=True)
    differ = 0
    for name in data.SNAPSHOT_FILES:
        src, dst = data.NIGHT / name, target / name
        if not src.exists():
            print(f"missing    {name}")
            continue
        new = src.read_bytes()
        old = dst.read_bytes() if dst.exists() else None
        if new == old:
            print(f"same       {name}  ({len(new)} bytes)")
            continue
        differ += 1
        if check:
            print(f"DIFFERS    {name}: night {len(new)} bytes, snapshot {len(old) if old is not None else 'none'}")
        else:
            dst.write_bytes(new)
            print(f"copied     {name}  ({len(new)} bytes{'' if old is None else ', was ' + str(len(old))})")
    return 1 if check and differ else 0


if __name__ == "__main__":
    sys.exit(main())
