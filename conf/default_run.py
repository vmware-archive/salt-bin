# -*- coding: utf-8 -*-
#!/usr/bin/env python3

# Import python libs
import sys

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
    if salt.utils.platform.is_windows():
        # Since this file does not have a '.py' extension, when running on
        # Windows, spawning any addional processes will fail due to Python
        # not being able to load this 'module' in the new process.
        # Work around this by creating a '.pyc' file which will enable the
        # spawned process to load this 'module' and proceed.
        import os.path
        import py_compile
        cfile = os.path.splitext(__file__)[0] + '.pyc'
        if not os.path.exists(cfile):
            py_compile.compile(__file__, cfile)
    redirect()
