#!/usr/bin/python3
import sys
import os
import shutil
import subprocess
import tempfile
import tarfile
import venv
import argparse

OMIT = ('__pycache__', 'PyInstaller', 'pip', 'setuptools', 'pkg_resources', '__pycache__', 'dist-info', 'egg-info')

PKGINFO = '''Metadata-Version: 1.1
Name: saltbin
Version: {}
Summary: Salt System Management all in one binary
Home-page: UNKNOWN
Author: UNKNOWN
Author-email: UNKNOWN
License: UNKNOWN
Description: UNKNOWN
Platform: UNKNOWN
Classifier: Operating System :: OS Independent
Classifier: Programming Language :: Python
Classifier: Programming Language :: Python :: 3.6
Classifier: Programming Language :: Python :: 3.7
Classifier: Development Status :: 5 - Production/Stable
'''


def parse():
    '''
    Parse the cli args
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument(
            '--name',
            '-n',
            default='salt',
            help='The name of the script to build')
    parser.add_argument(
            '--salt-version',
            '-s',
            dest='sver',
            default='',
            help='The version of Salt to build',
            )
    parser.add_argument(
            '-r',
            '--requirements',
            default='requirements.txt',
            help='The path to the requirements.txt file to use to populate the build environment',
            )
    parser.add_argument(
            '--exclude',
            '-e',
            default='exclude.txt',
            help='The path to the exclude file, these packages will be removed after install'
            )
    args = parser.parse_args()
    return args.__dict__


class Builder:
    def __init__(self):
        self.opts = parse()
        self.name = self.opts['name']
        self.cwd = os.getcwd()
        self.run = os.path.join(self.cwd, 'run.py')
        self.venv_dir = tempfile.mkdtemp(prefix='pop_', suffix='_venv')
        self.python_bin = os.path.join(self.venv_dir, 'bin', 'python')
        self.vroot = os.path.join(self.venv_dir, 'lib')
        self.mver = self.__get_meta_ver()
        self.req = self.__mk_requirements()
        self.all_paths = set()
        self.imports = set()
        self.datas = set()
        self.cmd = f'{self.python_bin} -B -OO -m PyInstaller '
        self.s_path = os.path.join(self.venv_dir, 'bin', self.name)
        self.pyi_args = [
              self.s_path,
              '--log-level=INFO',
              '--noconfirm',
              '--onefile',
              '--clean',
            ]

    def __get_meta_ver(self):
        vstr = subprocess.run('pip search salt', check=True, stdout=subprocess.PIPE, shell=True).stdout
        final = ''
        for line in vstr.split(b'\n'):
            if line.startswith(b'salt ('):
                final = line.decode()
        return final[final.index('(') + 1: final.rindex(')')]

    def __mk_requirements(self):
        req = os.path.join(self.cwd, '__build_requirements.txt')
        with open(self.opts['requirements'], 'r') as rfh:
            data = rfh.read()
            if self.opts['sver']:
                data += f'\nsalt=={self.opts["sver"]}'
            else:
                data += 'salt'
        with open(req, 'w+') as wfh:
            wfh.write(data)
        return req

    def create(self):
        '''
        Make a virtual environment based on the version of python used to call this script
        '''
        venv.create(self.venv_dir, clear=True, with_pip=True)
        pip_bin = os.path.join(self.venv_dir, 'bin', 'pip')
        subprocess.call([pip_bin, 'install', '-r', self.req])
        subprocess.call([pip_bin, 'install', 'PyInstaller'])
        subprocess.call([pip_bin, 'uninstall', '-y', '-r', self.opts['exclude']])

    def omit(self, test):
        for bad in OMIT:
            if bad in test:
                return True
        return False

    def scan(self):
        '''
        Scan the new venv for files and imports
        '''
        for root, dirs, files in os.walk(self.vroot):
            if self.omit(root):
                continue
            for d in dirs:
                full = os.path.join(root, d)
                if self.omit(full):
                    continue
                self.all_paths.add(full)
            for f in files:
                full = os.path.join(root, f)
                if self.omit(full):
                    continue
                self.all_paths.add(full)

    def to_import(self, path): 
        ret = path[path.index('site-packages') + 14:].replace(os.sep, '.')
        if ret.endswith('.py'):
            ret = ret[:-3]
        return ret

    def to_data(self, path):
        dest = path[path.index('site-packages') + 14:]
        src = path
        if not dest.strip():
            return None
        ret = f'{src}{os.pathsep}{dest}'
        return ret

    def mk_adds(self):
        '''
        make the imports and datas for pyinstaller
        '''
        for path in self.all_paths:
            if not 'site-packages' in path:
                continue
            if os.path.isfile(path):
                if not path.endswith('.py'):
                    continue
                if path.endswith('__init__.py'):
                    # Skip it, we will get the dir
                    continue
                imp = self.to_import(path)
                if imp:
                    self.imports.add(imp)
            if os.path.isdir(path):
                data = self.to_data(path)
                imp = self.to_import(path)
                if imp:
                    self.imports.add(imp)
                if data:
                    self.datas.add(data)

    def mk_cmd(self):
        '''
        Create the pyinstaller command
        '''
        for imp in self.imports:
            self.pyi_args.append(f'--hidden-import={imp}')
        for data in self.datas:
            self.pyi_args.append(f'--add-data={data}')
        for arg in self.pyi_args:
            self.cmd += f'{arg} '

    def pyinst(self):
        shutil.copy(self.run, self.s_path)
        subprocess.call(self.cmd, shell=True)

    def static(self):
        '''
        Make the binary static by removing dynamic linking refs and
        embedding the dynamic libs
        '''
        print('Statically linking binary')
        subprocess.call(['staticx', 'dist/salt', 'dist/salt'])

    def mk_tar(self):
        '''
        Create the distribution tarball for this binary that can be used by
        pypi
        '''
        with open('PKG-INFO', 'w+') as wfh:
            wfh.write(PKGINFO.format(self.mver))
        tname = f'dist/saltbin-{self.mver}.tar.gz'
        with tarfile.open(tname, 'w:gz') as tfh:
            tfh.add('PKG-INFO')
            tfh.add('dist/salt', arcname=f'salt-{self.mver}')

    def report(self):
        art = os.path.join(self.cwd, 'dist', self.name)
        print(f'Executable created in {art}')

    def clean(self):
        shutil.rmtree(self.venv_dir)
        shutil.rmtree(os.path.join(self.cwd, 'build'))
        os.remove(os.path.join(self.cwd, f'{self.name}.spec'))
        os.remove(self.req)
        os.remove('PKG-INFO')

    def build(self):
        self.create()
        self.scan()
        self.mk_adds()
        self.mk_cmd()
        self.pyinst()
        self.static()
        self.mk_tar()
        self.report()
        self.clean()


if __name__ == '__main__':
    builder = Builder()
    builder.build()