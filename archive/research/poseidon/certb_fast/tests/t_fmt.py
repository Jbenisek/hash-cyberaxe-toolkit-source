import sys; sys.path.insert(0,'tests'); sys.path.insert(0, r'../../../3rd_openai_workspace/luna3')
from fh import *
import P3_22_bsgs as b
from pathlib import Path
d='tests/data/cert_pos101'
f=to_poly(read_poly(d+'/f.bin'))
b.write_poly_artifact(Path('tests/data/ref_f.txt'), f, {"center": 12345, "line": 0, "trial": 0, "role": "factor"})
print('format identical:', open('tests/data/ref_f.txt','rb').read()==open(d+'/certB_witness_f.txt','rb').read())
