"""Export a held-subset system in the ../ksplit sysfile format (N E NM F, names, eqs), plain model (NM = 0),
so that ../ksplit/rootcore.py (read only) can test the join-tree root condition for the k = 3 sphere level.
Usage: python export_sys.py out0,out2,out5 sys_k3_025.txt
"""
import sys

from build import system
from cores import incid


def main():
    held = tuple(sys.argv[1].split(","))
    eqs, const, _ = system(held=held)
    E, occ = incid(eqs, const)
    names = sorted(occ)
    ix = {v: i for i, v in enumerate(names)}
    F = len(names) - len(eqs)
    with open(sys.argv[2], "w") as f:
        f.write(f"{len(names)} {len(eqs)} 0 {F}\n")
        f.write("\n".join(names) + "\n")
        for (nm, _), e in zip(eqs, E):
            f.write(f"{nm} {len(e)} " + " ".join(str(ix[v]) for v in sorted(e)) + "\n")
    print(sys.argv[2], "words", len(names), "eqs", len(eqs), "F", F)


if __name__ == "__main__":
    main()
