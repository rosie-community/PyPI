#!/bin/bash
python_bin=$1
default="python"
if [ -z "$python_bin" ]; then
    echo "Using default python executable: $default"
    echo "To use a different python, use: `basename $0` python_executable_name" 
    python_bin=$default
fi
cd /tmp
echo ""
echo "Testing in directory `pwd` with `$python_bin --version 2>&1`"
$python_bin -c <<EOF '
from __future__ import print_function
import rosie, json
e = rosie.engine()
for parms in json.loads(e.config()):
    for parm in parms:
        print(parm["name"], parm["value"])
print("Installation ok")
'
EOF
