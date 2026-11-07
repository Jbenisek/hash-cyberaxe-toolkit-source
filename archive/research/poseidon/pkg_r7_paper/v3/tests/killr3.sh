#!/bin/bash
for p in $(pgrep -x single_r3); do kill $p; done
sleep 1; echo remaining $(pgrep -x single_r3 | wc -l)
