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

LATEST = 'salt'


def scan():
    data = {}
    for root, dirs, files in os.walk('dist'):
        if root == 'dist':
            continue
        base = os.path.basename(root)
        data[base] = {}
        for fn in files:
            if fn == LATEST:
                continue
            data[base][fn] = {
                    'name': fn,
                    'version': fn[fn.index('-')+1:]
                    }
            full = os.path.join(root, fn)
            with open(full, 'rb') as rfh:
                raw = rfh.read()
                data[base][fn]['blake'] = hashlib.blake2b(raw).hexdigest()
                data[base][fn]['sha512'] = hashlib.sha512(raw).hexdigest()
                data[base][fn]['sha3_512'] = hashlib.sha3_512(raw).hexdigest()

    for base, rels in data.items():
        names = []
        for fn, rel in rels.items():
            names.append(rel['version'])
        names = sorted(names, key=StrictVersion)
        latest = os.path.join(f'salt-{names[-1]}')
        latest_lk = os.path.join('dist', base, 'salt')
        if os.path.exists(latest_lk):
            os.remove(latest_lk)
        os.symlink(latest, latest_lk)
    with open('dist/repo.mp', 'wb+') as wfh:
        wfh.write(msgpack.dumps(data))
    with open('dist/repo.json', 'w+') as wfh:
        wfh.write(json.dumps(data))


scan()
