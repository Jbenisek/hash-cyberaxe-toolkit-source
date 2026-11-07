cd "$(dirname "$0")"
date > run.log
timeout 900 ./scan bucket 0 31 7370401 --threads 4 > bucket0.out 2>&1; echo "b0 rc $?" >> run.log
timeout 400 ./scan bucket 1 29 7370402 --threads 4 > bucket1.out 2>&1; echo "b1 rc $?" >> run.log
timeout 400 ./scan bucket 2 29 7370403 --threads 4 > bucket2.out 2>&1; echo "b2 rc $?" >> run.log
timeout 400 ./scan bucket 3 29 7370404 --threads 4 > bucket3.out 2>&1; echo "b3 rc $?" >> run.log
timeout 400 ./scan bucket 4 29 7370405 --threads 4 > bucket4.out 2>&1; echo "b4 rc $?" >> run.log
timeout 700 ./scan real 29 7370406 --threads 4 > real.out 2>&1; echo "real rc $?" >> run.log
date >> run.log; echo DONE >> run.log
