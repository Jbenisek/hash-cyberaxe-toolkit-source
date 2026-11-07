pkill -f "kissat -q r_outhalf_DCEo_T2_S10.cnf"
sleep 1
ps -eo etime,args | grep -E "[k]issat -q (r_|s_)|[b]dp|[b]d sa|[z]3 -smt2" | grep -v timeout
