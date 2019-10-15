'''
Create the repo files used by heist to read what files are available
'''
# Import python libs
import os
import json
import pprint
import hashlib
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
            if fn.endswith(('sha512', 'blake', 'salt', 'sha3_512')):
                continue
            data[base].append(fn)
    for root, dirs, files in os.walk('dist'):
        if root == 'dist':
            continue
        for fn in files:
            full = os.path.join(root, fn)
            sha512_p = f'{full}.sha512'
            sha_3_512_p = f'{full}.sha3_512'
            blake_p = f'{full}.blake'
            with open(full, 'rb') as rfh:
                raw = rfh.read()
                blake_digest = hashlib.blake2b(raw).hexdigest()
                sha512_digest = hashlib.sha512(raw).hexdigest()
                sha_3_512_digest = hashlib.sha3_512(raw).hexdigest()
            with open(sha512_p, 'w+') as wfh:
                wfh.write(sha512_digest)
            with open(sha_3_512_p, 'w+') as wfh:
                wfh.write(sha_3_512_digest)
            with open(blake_p, 'w+') as wfh:
                wfh.write(blake_digest)
    for base, rels in data.items():
        names = []
        for rel in rels:
            names.append(rel[rel.index('-')+1:])
        names = sorted(names, key=StrictVersion)
        latest = os.path.join(f'salt-{names[-1]}')
        latest_lk = os.path.join('dist', base, 'salt')
        os.symlink(latest, latest_lk)
    with open('dist/repo.mp', 'wb+') as wfh:
        wfh.write(msgpack.dumps(data))
    with open('dist/repo.json', 'w+') as wfh:
        wfh.write(json.dumps(data))


scan()
