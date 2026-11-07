#!/bin/bash
uptime
ps -eo pid,etimes,pcpu,args --sort=-pcpu | head -25
