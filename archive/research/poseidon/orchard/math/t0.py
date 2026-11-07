from pos import *
v = json.load(open(ROOT + r'\tests\orchard-upstream-vectors.json'))
print(v.keys())
ok = 0
for row in v['permute']:
    x = [int.from_bytes(bytes.fromhex(h), 'little') for h in row]
    out = full_perm(x[:3])
    ok += out == x[3:]
print('permute vectors ok', ok, '/', len(v['permute']))
print('p mod 5', p % 5, 'gcd(5,p-1)', __import__('math').gcd(5, p - 1), '2-adicity', ((p-1) & -(p-1)).bit_length()-1)
for k in v:
    print(k, len(v[k]))
