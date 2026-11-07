#!/bin/bash
ps -eo pcpu,etime,args --sort=-pcpu | grep -E 'bf|kissat|cadical|cryptominisat' | grep -v -E 'grep|timeout|bash'
