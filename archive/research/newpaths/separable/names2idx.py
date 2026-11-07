"""Convert guess-name lists to 'FULL k=..: idx..' lines for jtree.  Usage: python names2idx.py sys.txt "n1 n2 .." ..."""
import sys

lines = open(sys.argv[1]).read().split("\n")
N = int(lines[0].split()[0])
names = lines[1:1 + N]
idx = {v: i for i, v in enumerate(names)}
for arg in sys.argv[2:]:
    ws = arg.split()
    print(f"FULL k={len(ws)}: " + " ".join(str(idx[w]) for w in ws))
