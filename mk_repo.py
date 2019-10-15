'''
Create the repo files used by heist to read what files are available
'''
# Import python libs
import os
import json
import pprint
from distutils.version import StrictVersion

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
    for base, rels in data.items():
        names = []
        for rel in rels:
            names.append(rel[rel.index('-')+1:])
        names = sorted(names, key=StrictVersion)
        latest = os.path.join(f'salt-{names[-1]}')
        latest_lk = os.path.join('dist', base, 'latest')
        os.symlink(latest, latest_lk)
    with open('dist/repo.mp', 'wb+') as wfh:
        wfh.write(msgpack.dumps(data))
    with open('dist/repo.json', 'w+') as wfh:
        wfh.write(json.dumps(data))


scan()
