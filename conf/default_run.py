# -*- coding: utf-8 -*-
#!/usr/bin/env python3

# Import python libs
import sys
import multiprocessing

# Import salt libs
import salt.scripts
import salt.utils.platform

AVAIL = (
        'minion',
        'master',
        'call',
        'api',
        'cloud',
        'cp',
        'extend',
        'key',
        'proxy',
        'run',
        'ssh',
        'support',
        'syndic',
        )


def redirect():
    '''
    Change the args and redirect to another salt script
    '''
    if len(sys.argv) < 2:
        msg = 'Must pass in a salt command, available commands are:'
        for cmd in AVAIL:
            msg += '\n{0}'.format(cmd)
        print(msg)
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd not in AVAIL:
        # Fall back to the salt command
        sys.argv[0] = 'salt'
        s_fun = salt.scripts.salt_main
    else:
        sys.argv[0] = 'salt-{0}'.format(cmd)
        sys.argv.pop(1)
        s_fun = getattr(salt.scripts, 'salt_{0}'.format(cmd))
    s_fun()


if __name__ == '__main__':
    if sys.platform.startswith('win'):
        multiprocessing.freeze_support()
    redirect()
