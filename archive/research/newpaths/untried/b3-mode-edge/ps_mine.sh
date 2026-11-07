#!/bin/sh
# List this scout's own kpipe processes (PID, elapsed, command) and the clock.
date +%T
ps -eo pid,etime,pcpu,args | grep "[k]pipe" || echo "no kpipe process"
