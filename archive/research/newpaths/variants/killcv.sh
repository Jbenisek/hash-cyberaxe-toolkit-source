#!/bin/bash
pkill -f "cv_run.sh"; pkill -f "gdcv models"; sleep 1; ps -eo args | grep gdcv | grep -v grep | head -2
