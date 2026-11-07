s = open('certb_fast.cu', encoding='utf-8', newline='').read()
i = s.index('gcd_g_gprime_degree')
j = s.index('sqf);', i)
bs = chr(92)
new = 'gcd_g_gprime_degree' + bs + '":%d}' + bs + 'n", sqf);'
s = s[:i] + new + s[j + 5:]
open('certb_fast.cu', 'w', encoding='utf-8', newline='').write(s)
