t = open('proof_template.md').read()
a = "(computed; so `deg F = D` exactly). For random"
assert t.count(a) == 1
b = ("(computed; so `deg F = D` exactly). The program reaches the same value from the other side: the inverse transform of stage B returns `H g_m = @@LEAD@@` "
     "(`H = @@H@@`), and `(H g_m) / H = f_D(0)`; stage B tests that coefficient for zero with a counted test before it inverts it. For random")
open('proof_template.md', 'w', newline='\n').write(t.replace(a, b))
s = open('build_package.py').read()
a2 = "FD0='0x13f08536819885e275e9b4b9c9c3aaaf453220a766fbe69710da897c392caa6f')"
assert s.count(a2) == 1
s = s.replace(a2, "FD0='0x13f08536819885e275e9b4b9c9c3aaaf453220a766fbe69710da897c392caa6f', LEAD='0x0fa384c991a761bd1e2d5d4b000daf8d19d5135a4c285102896c07b7ff4c10ba')")
a3 = "'FD0': PAR['FD0'],"
assert s.count(a3) == 1
s = s.replace(a3, "'FD0': PAR['FD0'], 'LEAD': PAR.get('LEAD', ''),")
a4 = "assert m == (PAR['D'] - 1) // 2"
assert s.count(a4) == 1
s = s.replace(a4, a4 + "\nP_ = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001\nif R == 2: assert int(PAR['LEAD'], 16) * pow(PAR['H'], -1, P_) % P_ == int(PAR['FD0'], 16)")
open('build_package.py', 'w', newline='\n').write(s)
print('ok')
