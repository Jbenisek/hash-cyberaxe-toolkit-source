#!/bin/bash
pkill -f "kissat -q sph_out5_k15.cnf"
pkill -f "kissat -q sph_out7_k15.cnf"
sleep 1
ps aux | grep "sph_out" | grep -v grep | wc -l