cd /root/b4c || exit 1
export PYTHONDONTWRITEBYTECODE=1
pip install --target /root/b4c/lib blake3==1.0.11 >/root/b4c/pip.log 2>&1 || pip install --target /root/b4c/lib blake3 >>/root/b4c/pip.log 2>&1
LIB=/root/b4c/lib
./gen_native > gen_out.bin
( nice -n 19 python3 -B ext/exec_records.py /root/b4c exp gen_out.bin > exec_records.out 2>&1; nice -n 19 python3 -B ext/ref_regress.py /root/b4c exp > ref_regress.out 2>&1 ) &
( nice -n 19 python3 -B ext/ref_check.py /root/b4c exp $LIB > ref_check.out 2>&1; nice -n 19 python3 -B exp/bsrho.py --selftest > selftest.out 2>&1 ) &
wait
echo done > DONE
