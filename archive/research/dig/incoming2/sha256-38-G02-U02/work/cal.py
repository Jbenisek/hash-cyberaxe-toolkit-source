import pickle,time,a0lean38 as A
t=time.time(); cal=A.calibrate(); pickle.dump(cal,open('cal.pkl','wb')); print('cal',time.time()-t)
rows,info=A.ledger(cal); A.report(rows)
print(A.memory(cal)[1])
