import time
from pos_scan_lib import *
vec = open(os.path.join(IMPL, 'known_answers_reduced.txt')).read().split('\n')
ok = 0; n = 0
for l in vec:
    f = l.split()
    if len(f) >= 5 and f[0].isdigit():
        r, nk, rho = int(f[0]), int(f[1]), int(f[2])
        # file columns: nk rho r out_hex out_le_hex
        out = int(f[3], 16)
        n += 1; ok += hash_reduced(nk, rho, r) == out
print('ref vectors', ok, '/', n)
for r in (0, 1, 2):
    for j in range(3):
        t = time.time(); sp = specs_from_2(r)
        alpha, beta, line = line_affine(j)
        print(r, j, W_deg(alpha, beta, sp), 5 ** (6 + r), round(time.time() - t, 3))
