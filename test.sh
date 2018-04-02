#!/bin/bash
cd /tmp
echo "Testing in directory `pwd` with `python --version 2>&1`"
python -c <<EOF '
from __future__ import print_function
import rosie, json
e = rosie.engine()
for parms in json.loads(e.config()):
    for parm in parms:
        print(parm["name"], parm["value"])
print("Installation ok")
'
EOF
