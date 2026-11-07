#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
ps -eo pid,etimes,stat,args | grep r39joint | grep -v grep | head -5; echo "n=$(ps -eo args | grep r39joint | grep -vc grep)"; free -g | head -2; ls -la "${HASHCYBERAXE_WORKSPACE}"/research/pkg_r39_vars/7111e7edc4/led/ | head -4
