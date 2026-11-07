import sys; sys.argv=['x','none','99']
exec(open('scan.py').read().replace("\nmain()\n","\n"))
res=[]
for s in range(2):
    run("k2 w7,11 (2^22)",fam_words([7,11],1<<22),res)
run("k2 w0,12 (2^22)",fam_words([0,12],1<<22),res)
