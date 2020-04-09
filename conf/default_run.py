# -*- coding: utf-8 -*-
#!/usr/bin/env python3

# Import python libs
import sys
import os
import multiprocessing

# Import salt libs
import salt.scripts
import salt.utils.platform

# Import third party libs
from pip._internal.cli.main import main


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
        'pip',
        'run',
        'shell',
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
    if cmd == "shell":
        py_shell()
        return
    elif cmd == "pip":
        pip()
        return
    elif cmd not in AVAIL:
        # Fall back to the salt command
        sys.argv[0] = 'salt'
        s_fun = salt.scripts.salt_main
    else:
        sys.argv[0] = 'salt-{0}'.format(cmd)
        sys.argv.pop(1)
        s_fun = getattr(salt.scripts, 'salt_{0}'.format(cmd))
    s_fun()


def py_shell():
    import readline # optional, will allow Up/Down/History in the console
    import code
    variables = globals().copy()
    variables.update(locals())
    shell = code.InteractiveConsole(variables)
    shell.interact()


def pip():
    cmd = sys.argv[2]
    args = [cmd, '--target', sys._MEIPASS,]
    args.extend(sys.argv[3:])
    parser = ['pip'] + args
    sys.argv = parser
    main(args)


if __name__ == '__main__':
    if sys.platform.startswith('win'):
        multiprocessing.freeze_support()
    redirect()
