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


SPEC = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis([r'{s_path}'],
             pathex=[r'{cwd}'],
             binaries=[],
             datas={datas},
             hiddenimports={imports},
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='salt',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
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
    parser.add_argument(
            '--system-site',
            '-S',
            default=False,
            action='store_true',
            dest='sys_site',
            help='Include the system site-packages when building. This is needed for builds from custom installs of python.',
            )
    parser.add_argument(
            '--use-spec',
            '-U',
            dest='spec',
            default=False,
            action='store_true',
            help='Instead of running PyInstaller completely from the cli generate a spec file, required for Windows',
            )
    args = parser.parse_args()
    return args.__dict__


class Builder(object):

    def __init__(
            self, name, requirements, sver, sys_site, exclude, spec,
            work_dir=os.getcwd(), venv_dir=tempfile.mkdtemp(), is_win=False,
        ):
        self.name = name
        self.requirements = requirements
        self.sver = sver
        self.sys_site = sys_site
        self.exclude = exclude
        self.spef = spec
        self.work_dir = work_dir
        self.is_win = is_win
        self.venv_dir = venv_dir
        if self.is_win:
            self.python_bin = os.path.join(self.venv_dir, 'Scripts', 'python')
            self.s_path = os.path.join(self.venv_dir, 'Scripts', self.name)
        else:
            self.python_bin = os.path.join(self.venv_dir, 'bin', 'python')
            self.s_path = os.path.join(self.venv_dir, 'bin', self.name)
        self.vroot = os.path.join(self.venv_dir, 'lib')
        self.mver = self.__get_meta_ver()
        self.req = self.__mk_requirements()
        self.all_paths = set()
        self.imports = set()
        self.datas = set()
        self.cmd = f'{self.python_bin} -B -OO -m PyInstaller '
        self.pyi_args = [
              self.s_path,
              '--log-level=INFO',
              '--noconfirm',
              '--onefile',
              '--clean',
            ]

    @property
    def run(self):
        return os.path.join(self.work_dir, 'run.py')

    @property
    def spec(self):
        return os.path.join(self.work_dir, f'{self.name}.spec')

    def __get_meta_ver(self):
        vstr = subprocess.run('pip3 search salt', check=True, stdout=subprocess.PIPE, shell=True).stdout
        final = ''
        for line in vstr.split(b'\n'):
            if line.startswith(b'salt ('):
                final = line.decode()
        return final[final.index('(') + 1: final.rindex(')')]

    def __mk_requirements(self):
        req = os.path.join(self.work_dir, '__build_requirements.txt')
        with open(self.requirements, 'r') as rfh:
            data = rfh.read()
            # TODO: configure this via environment or config file?
            if 'git+https://github.com/Ch3LL/salt.git@2019.2.2' in data:
                pass
            elif self.sver:
                data += f'\nsalt=={self.sver}'
            else:
                data += 'salt'
        with open(req, 'w+') as wfh:
            wfh.write(data)
        return req

    def create(self):
        '''
        Make a virtual environment based on the version of python used to call this script
        '''
        venv.create(self.venv_dir, clear=True, with_pip=True, system_site_packages=self.sys_site)
        if os.name == 'nt':
            py_bin = os.path.join(self.venv_dir, 'Scripts', 'python')
        else:
            py_bin = os.path.join(self.venv_dir, 'bin', 'python3')
        pip_cmd = f'{py_bin} -m pip '
        subprocess.run(f'{pip_cmd} install -r {self.req}', shell=True)
        # Install old pycparser to fix: https://github.com/eliben/pycparser/issues/291 on Windows
        subprocess.run(f'{pip_cmd} install pycparser==2.14', shell=True)
        subprocess.run(f'{pip_cmd} install PyInstaller', shell=True)
        subprocess.run(f'{pip_cmd} uninstall -y -r {self.exclude}', shell=True)

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

    def mk_spec(self):
        '''
        Create a spec file to build from
        '''
        datas = []
        imps = []
        kwargs = {
                's_path': self.s_path,
                'cwd': self.work_dir,
                }
        for imp in self.imports:
            imp = imp.replace('\\', '\\\\')
            imps.append(imp)
        for data in self.datas:
            src, dst = data.split(os.pathsep)
            src = src.replace('\\', '\\\\')
            dst = dst.replace('\\', '\\\\')
            datas.append((src, dst))
        kwargs['datas'] = datas.__repr__()
        kwargs['imports'] = imps.__repr__()
        spec = SPEC.format(**kwargs)
        with open(self.spec, 'w+') as wfh:
            wfh.write(spec)
        self.cmd += f' {self.spec}'

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
        dname = os.path.dirname(self.s_path)
        if not os.path.isdir(dname):
            os.makedirs(os.path.dirname(self.s_path))
        shutil.copy(self.run, self.s_path)
        subprocess.call(self.cmd, shell=True)

    def mk_tar(self):
        '''
        Create the distribution tarball for this binary that can be used by
        pypi
        '''
        with open('PKG-INFO', 'w+') as wfh:
            wfh.write(PKGINFO.format(self.mver))
        tname = os.path.join('dist', f'saltbin-{self.mver}.tar.gz')
        with tarfile.open(tname, 'w:gz') as tfh:
            tfh.add('PKG-INFO')
            tfh.add(os.path.join('dist', 'salt'), arcname=f'salt-{self.mver}')

    def mv_final(self):
        shutil.move('dist/salt', f'dist/salt-{self.mver}')

    def report(self):
        art = os.path.join(self.work_dir, 'dist', self.name)
        print(f'Executable created in {art}')

    def clean(self):
        shutil.rmtree(self.venv_dir)
        shutil.rmtree(os.path.join(self.work_dir, 'build'))
        os.remove(self.spec)
        os.remove(self.req)
        os.remove('PKG-INFO')

    def build(self):
        self.create()
        self.scan()
        self.mk_adds()
        if self.spec:
            self.mk_spec()
        else:
            self.mk_cmd()
        self.pyinst()
        self.mk_tar()
        self.mv_final()
        self.report()
        self.clean()


if __name__ == '__main__':
    opts = parse()
    builder = Builder(
        opts['name'], opts['requirements'], opts['sys_site'], opts['exclude'],
        opts['spec'], os.getcwd(), is_win=os.name == 'nt',
    )
    builder.build()
