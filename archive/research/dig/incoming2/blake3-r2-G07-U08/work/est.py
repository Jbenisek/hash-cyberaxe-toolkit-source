import os,glob,sys
pkg=sys.argv[1]; proofp=sys.argv[2]
T=os.path.join(pkg,'blake3-r2')
proof=open(proofp,encoding='utf-8',newline='').read()
shipped=[f for f in glob.glob(os.path.join(T,'**','*'),recursive=True) if os.path.isfile(f) and '__pycache__' not in f]
est=len(proof.encode())+9*proof.count('\n')+sum(os.path.getsize(f) for f in shipped if not f.endswith('proof.md'))
est+=os.path.getsize(os.path.join(pkg,'submission-note-r2.md'))+os.path.getsize(os.path.join(pkg,'dependencies.json'))
print(proofp,est,'spare',524288-est)
