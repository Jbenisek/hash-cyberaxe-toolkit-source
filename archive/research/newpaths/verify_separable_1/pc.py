# positive control helper: pair index (my decreasing-order enumeration) of a known 8-set's two largest indices
import sys
lines = open(r"my_fixed.txt").read().split("\n")
N, E = map(int, lines[0].split()[:2])
eqs = [set(map(int, l.split()[2:])) for l in lines[1 + N:1 + N + E]]
def cl(K):
    K = set(K)
    while True:
        ch = False
        for e in eqs:
            u = e - K
            if len(u) == 1:
                K |= u; ch = True
        if not ch:
            return K
S = list(map(int, open(r"../separable/k8_sample200k.txt").readline().split(":")[1].split()))
assert len(cl(S)) == N, "known set not full under my closure"
s = sorted(S, reverse=True)
pi = 0
for i in range(N - 1, -1, -1):
    K1 = cl([i])
    if len(K1) == N:
        continue
    for j in range(i - 1, -1, -1):
        if j in K1:
            continue
        if (i, j) == (s[0], s[1]):
            print(pi, S); sys.exit()
        pi += 1
