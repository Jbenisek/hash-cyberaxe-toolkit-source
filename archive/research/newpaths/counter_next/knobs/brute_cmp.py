"""brute_cmp.py: compare the bit search (brute_cases.txt, e3dfs partial) with the 2^32 brute force (brute_out_*.txt)."""
cases = [ln.split() for ln in open('brute_cases.txt') if not ln.startswith('#')]
allok = True
for i, p in enumerate(cases):
    dfs = set()
    if int(p[3]):
        dfs = {(int(a, 16), int(b)) for a, b in (q.split(':') for q in p[5].split(','))}
    bf = set()
    cnt = None
    for ln in open(f'brute_out_{i}.txt'):
        if ln.startswith('# count'):
            cnt = int(ln.split()[2])
        else:
            a, b = ln.split()
            bf.add((int(a, 16), int(b)))
    ok = dfs == bf and cnt == len(bf)
    allok &= ok
    print(f'case {i} (y {p[0]} Y9 {p[1]} w8 {p[2]}): search {len(dfs)}, brute force {len(bf)} (count line {cnt}); '
          f'identical sets: {ok}; search nodes {p[4]}')
print('ALL IDENTICAL' if allok else 'MISMATCH')
