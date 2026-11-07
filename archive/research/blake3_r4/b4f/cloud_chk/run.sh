# runs on the cloud box under /root/b3r4f ; nice 10 ; own PIDs only
cd /root/b3r4f || exit 1
export PYTHONDONTWRITEBYTECODE=1
pip install --target /root/b3r4f/lib blake3==1.0.11 > pip.log 2>&1 || pip install --target /root/b3r4f/lib blake3 >> pip.log 2>&1
nice -n 10 python3 -B ext/ref_check.py /root/b3r4f exp /root/b3r4f/lib > ref_check.out 2>&1
nice -n 10 python3 -B ext/ref_regress.py /root/b3r4f exp > ref_regress.out 2>&1
nice -n 10 python3 -B ext/rolled_listing_check.py exp > rolled_listing.out 2>&1
nice -n 10 python3 -B exp/bsrho.py --selftest > selftest.out 2>&1
nice -n 10 python3 -B exp/bsrho.py --ledger > ledger.out 2>&1
echo done > DONE
