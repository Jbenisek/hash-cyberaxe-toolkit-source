cd "$(dirname "$0")"
( time nice -n 19 python3 -B appA.py > appA.out.new 2> appA.err ) 2> appA.time
