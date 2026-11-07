cd /root/b4
( ulimit -s 64; nice -n 19 /usr/bin/time -v -o /root/b4/time.txt ./single 1 > /root/b4/run.txt 2>&1; echo "EXIT $?" >> /root/b4/run.txt )