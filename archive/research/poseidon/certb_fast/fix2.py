s = open('certb_fast.cu', encoding='utf-8', newline='').read()
bs = chr(92)
old = '"  ' + bs + '"rabin_result' + bs + '": ' + bs + '"%s' + bs + '"'
new = '"  ' + bs + '"squarefree_gcd_g_gprime_degree' + bs + '": %d,' + bs + 'n  ' + bs + '"rabin_result' + bs + '": ' + bs + '"%s' + bs + '"'
assert old in s
s = s.replace(old, new, 1)
open('certb_fast.cu', 'w', encoding='utf-8', newline='').write(s)
