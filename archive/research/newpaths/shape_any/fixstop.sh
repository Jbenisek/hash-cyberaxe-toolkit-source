K=$(pgrep -f "^kissat -q r_outhalf_DCEo_T2_S10.cnf")
echo "kissat pid $K"
[ -n "$K" ] && kill -STOP $K
ps -o pid,stat,args -p $K
