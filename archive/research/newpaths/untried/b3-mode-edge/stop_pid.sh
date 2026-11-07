#!/bin/sh
# Stop one of this scout's own processes by its PID (never by name).
kill "$1" && echo "stopped $1"
