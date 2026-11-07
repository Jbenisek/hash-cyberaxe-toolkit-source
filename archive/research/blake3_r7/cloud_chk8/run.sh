# runs on the cloud box under /root/b3roll8 ; nice 10 ; own PIDs only
cd /root/b3roll8 || exit 1
export PYTHONDONTWRITEBYTECODE=1
pip install --target /root/b3roll8/lib blake3==1.0.11 >/root/b3roll8/pip.log 2>&1 || pip install --target /root/b3roll8/lib blake3 >>/root/b3roll8/pip.log 2>&1
LIB=/root/b3roll8/lib
for R in 6 5; do
  (
  cd r$R
  nice -n 10 python3 -B ext/ref_check.py /root/b3roll8 rolled $LIB > ref_check.out 2>&1
  nice -n 10 python3 -B ext/ref_regress.py /root/b3roll8 rolled > ref_regress.out 2>&1
  nice -n 10 python3 -B ext/rolled_vs_straight.py rolled straight 64 > rolled_vs_straight.out 2>&1
  nice -n 10 python3 -B rolled/bsrho.py --selftest > selftest.out 2>&1
  echo done > DONE
  ) &
done
wait
