cd /root/b3u5b_r7 || exit 1
export PYTHONDONTWRITEBYTECODE=1
pip install --target /root/b3u5b_r7/lib blake3==1.0.11 >/root/b3u5b_r7/pip.log 2>&1 || pip install --target /root/b3u5b_r7/lib blake3 >>/root/b3u5b_r7/pip.log 2>&1
LIB=/root/b3u5b_r7/lib
./gen_native > gen_out.bin
( nice -n 10 python3 -B ext/exec_records.py /root/b3u5b_r7 exp gen_out.bin > exec_records.out 2>&1 ) &
( nice -n 10 python3 -B ext/ref_check.py /root/b3u5b_r7 exp $LIB > ref_check.out 2>&1 ) &
( nice -n 10 python3 -B ext/ref_regress.py /root/b3u5b_r7 exp > ref_regress.out 2>&1 ) &
( nice -n 10 python3 -B ext/step_vs_lib.py exp $LIB > step_vs_lib.out 2>&1 ) &
( nice -n 10 python3 -B exp/bsrho.py --selftest > selftest.out 2>&1 ) &
wait
echo done > DONE
