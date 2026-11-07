import re
s = open('build_package.py').read()


def sub(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (a, s.count(a))
    s = s.replace(a, b)


sub("SRC_FILES = ['common.h', 'common.c', 'pallas.h', 'pallas.c', 'pallas_consts.h', 'attack.h', 'hgcd.h', 'ntt.c', 'gen_kern.py', 'ntt_kern.h', 'ntt_a3.h', 'poly.c', 'lean.c', 'line.c', 'split.c', 'hgcd.c', 'single.c']",
    "SRC_FILES = ['common.h', 'common.c', 'pallas.h', 'pallas.c', 'pallas_consts.h', 'attack.h', 'hgcd.h', 'gen_kern.py', 'ntt_kern.h', 'ntt.c', 'poly.c', 'lean.c', 'line.c', 'euclid.c', 'hgcd.c', 'exec_attack.c']")
sub("body = open(os.path.join(HERE, fn)).read().rstrip('\\n')",
    "body = open(os.path.join(HERE, 'src', fn), newline='').read().replace('\\r\\n', '\\n').rstrip('\\n')")
i = s.index("# the sites of the unrolled-loop macro")
j = s.index("colls = json.load")
s = s[:i] + s[j:]
sub("'FOR8_LIST': FOR8_LIST, ", "")
sub(" 'FOR8_SHORT': FOR8_SHORT,", "")
sub("os.path.join(HERE, 'proof_template_exec.md')", "os.path.join(HERE, 'proof_template.md')")
sub("'T_PERM': L(tm.group(9)),", "'T_PERM': L(tm.group(9)), 'T_HC': L(HC), 'PEAK_STAGE': PEAK_STAGE,")
sub("tm = re.search(", "HC = int(re.search(r'^HALFUNITS hc=(\\d+)', logtxt, re.M).group(1))\nPEAK_STAGE = [n.split(':')[0] if ':' in n else n for n in names if S_[n]['peak'] == HEAP][0]\ntm = re.search(")
i = s.index('"statement": "The counts of proof.md')
j = s.index('"scope":')
b = ('"statement": "The counts of proof.md sections 6 and 7 describe the executed program of proof.md section 9 under the stated rules: 1 per field operation (a Montgomery conversion is one multiplication), '
     '1 per element load or store, 1/2 per butterfly and per element of an unrolled loop for loop and address work (half units rounded up to a whole operation at the end of each stage visit), '
     '1 per other executed index or control operation, %d per reduced permutation evaluation, and a register file of 18 words of 256 bits per transform block (16 data words plus two working words: '
     'the twiddle operand and the butterfly temporary) as the only register assumption." % C,\n         ')
s = s[:i] + b + s[j:]
open('build_package.py', 'w', newline='\n').write(s)
print('ok')
