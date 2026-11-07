"""Condense a tree printed by bd/bdp (lines '+ J=.. list=.. |A|=.. |B|=.. [calls]' and '- eq') into a coarse
drawing: subtrees with |A| <= cut are shown as one line '[calls] list=r'; along chains where one child is
small the spine is printed as a path ("caterpillar").  Also classifies the shape.
Usage: python coarse.py <tree.txt> [cut]
"""
import re
import sys


def parse(lines):
    root = None
    stack = []
    for ln in lines:
        m = re.match(r"^(\s*)\+ J=(\d+) list=(-?\d+) \|A\|=(\d+) \|B\|=(\d+)\s+\[(.*)\]", ln)
        m2 = re.match(r"^(\s*)- (\S+)", ln)
        if not m and not m2:
            continue
        depth = len((m or m2).group(1)) // 2
        node = ({"J": int(m.group(2)), "r": int(m.group(3)), "A": int(m.group(4)), "B": int(m.group(5)),
                 "calls": m.group(6), "kids": []} if m else
                {"J": 0, "r": 0, "A": 1, "B": 0, "calls": m2.group(2), "kids": []})
        while stack and stack[-1][0] >= depth:
            stack.pop()
        if stack:
            stack[-1][1]["kids"].append(node)
        else:
            root = node
        stack.append((depth, node))
    return root


def show(n, cut, ind, out):
    if n["A"] <= cut or not n["kids"]:
        out.append(f"{' ' * ind}[{n['calls']}] list={n['r']}")
        return
    out.append(f"{' ' * ind}JOIN J={n['J']} list={n['r']} |A|={n['A']} |B|={n['B']}")
    for k in sorted(n["kids"], key=lambda k: -k["A"]):
        show(k, cut, ind + 2, out)


def spine(n):
    """length of the heavy path and how many steps add a small (<= 8 eq) side."""
    steps = small = 0
    while n["kids"]:
        k = sorted(n["kids"], key=lambda k: -k["A"])
        steps += 1
        if len(k) > 1 and k[1]["A"] <= 8:
            small += 1
        n = k[0]
    return steps, small


def main():
    lines = open(sys.argv[1]).read().split("\n")
    cut = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    root = parse(lines)
    out = []
    show(root, cut, 0, out)
    print("\n".join(out))
    s, sm = spine(root)
    print(f"heavy path: {s} joins, {sm} of them add a side of <= 8 equations")


if __name__ == "__main__":
    main()
