'''
Create the repo files used by heist to read what files are available
'''
# Import python libs
import os
import json
import pprint

# Import third party libs
import msgpack


def scan():
    data = {}
    for root, dirs, files in os.walk('dist'):
        if root == 'dist':
            continue
        base = os.path.basename(root)
        data[base] = []
        for fn in files:
            data[base].append(fn)
    with open('dist/repo.mp', 'wb+') as wfh:
        wfh.write(msgpack.dumps(data))
    with open('dist/repo.json', 'w+') as wfh:
        wfh.write(json.dumps(data))


scan()
