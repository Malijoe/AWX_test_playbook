#!/usr/bin/env python
import argparse
import json
import os
import sys
from collections import defaultdict
from subprocess import PIPE, Popen
import re


ansi_escape = re.compile(r'''
    \x1B  # ESC
    (?:   # 7-bit C1 Fe (except CSI)
        [@-Z\\-_]
    |     # or [ for CSI, followed by a control sequence
        \[
        [0-?]*  # Parameter bytes
        [ -/]*  # Intermediate bytes
        [@-~]   # Final byte
    )
''', re.VERBOSE)

parser = argparse.ArgumentParser(description="Return Ansible inventory for one or more Ansible Tower instances")
parser.add_argument('--list', default=True, action="store_true",
                  help="Produce a JSON consumable grouping of Ansible Tower instances")
parser.add_argument('--host', action='store',
                  help="Generate additional host specific details for given host for Ansible")
args = parser.parse_args()

def _get_tower_instances():
    
    cmd = ['awx-manage','list_instances','--no-color']
    p = Popen(cmd, stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate()
    return p.returncode, stdout, stderr

if args.list:
    groups = defaultdict(list)
    hostvars = defaultdict(dict)
    (rc, response, eresponse) = _get_tower_instances()

    output = str(response.decode('utf-8'))
    output = ansi_escape.sub('',output)
    output = output.split('\n')
    group = ''

    for line in output:
        line = line.replace('\t','')
        if line == "":
            continue
        if '[' in line:
            parsed = line.replace('[','').replace(']','').split(' ')

            group = parsed[0]
            groups[group] = []
        else:
            hostname = line.split(' ')[0]
            groups[group].append(hostname)

    groups['_meta'] = dict(hostvars=hostvars)

    print(json.dumps(groups))
    sys.exit(0)

else: 
    parser.print_help()
    sys.exit(0)




