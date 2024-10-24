#!/bin/bash

RUNPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/bin
export DYLD_LIBRARY_PATH=/usr/local/bin
python3 $RUNPATH/run.py "$@"