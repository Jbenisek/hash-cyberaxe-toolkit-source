#!/bin/bash
ps -eo pid,ppid,etime,args | grep -E "worker.sh|ctr_toy8" | grep -v grep
