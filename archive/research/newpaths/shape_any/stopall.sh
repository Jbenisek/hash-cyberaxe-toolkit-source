# stop only this agent's own jobs (by their file names), then show what is left of mine
for s in brickp2.sh brickp.sh t11.sh t9.sh t7.sh calldp.sh cad.sh; do
  for p in $(ps -eo pid,args | grep "$s" | grep -v grep | awk '{print $1}'); do kill $p; done
done
pkill -f "kissat -q r_outhalf_T3_S10.cnf"
pkill -f "kissat -q s_outhalf_T2_S10.cnf"
pkill -f "kissat -q s_fixed_T2_S2.cnf"
pkill -f "bdp2 outhalf.sys brickp"
sleep 1
ps -eo etime,args | grep -E "shape_any|[k]issat -q (r_|s_|t_|pc_|lb)|[b]dp|[b]d2|[b]d3|[z]3 -smt2 z_" | grep -v grep
date
