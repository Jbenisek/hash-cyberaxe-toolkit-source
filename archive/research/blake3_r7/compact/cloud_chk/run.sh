cd /root/b3e || exit 1
export PYTHONDONTWRITEBYTECODE=1
pip install --target /root/b3e/lib blake3==1.0.11 >/root/b3e/pip.log 2>&1 || pip install --target /root/b3e/lib blake3 >>/root/b3e/pip.log 2>&1
LIB=/root/b3e/lib
./gen_native > gen_out.bin
( nice -n 10 python3 -B ext/exec_records.py /root/b3e exp gen_out.bin > exec_records.out 2>&1 ) &
( nice -n 10 python3 -B ext/ref_check.py /root/b3e exp $LIB > ref_check.out 2>&1 ) &
( nice -n 10 python3 -B ext/ref_regress.py /root/b3e exp > ref_regress.out 2>&1 ) &
( nice -n 10 python3 -B ext/step_vs_lib.py exp $LIB > step_vs_lib.out 2>&1 ) &
( nice -n 10 python3 -B exp/bsrho.py --selftest > selftest.out 2>&1 ) &
wait
echo done > DONE
