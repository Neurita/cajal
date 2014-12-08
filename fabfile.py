#!/usr/bin/env python

"""
Install the packages you have listed in the requirements file you input as
first argument.
"""
from   __future__ import (absolute_import, division, print_function, unicode_literals)

from   fabric.api import task, local, quiet

import os
import os.path    as     op
import subprocess
import shutil

from   fnmatch    import fnmatch
from   glob       import glob
from   setuptools import find_packages
from   pip.req    import parse_requirements

# Get version without importing, which avoids dependency issues
module_name    = find_packages(exclude=['tests'])[0]
version_pyfile = op.join(module_name, 'version.py')
exec(compile(open(version_pyfile).read(), version_pyfile, 'exec'))

# get current dir
CWD = op.realpath(op.curdir)

#ignore dirs
IGNORE = ['.git', '.idea']


def get_requirements(*args):
    """Parse all requirements files given and return a list of the dependencies"""
    install_deps = []
    try:
        for fpath in args:
            install_deps.extend([str(d.req) for d in parse_requirements(fpath)])
    except:
        print('Error reading {} file looking for dependencies.'.format(fpath))

    return [dep for dep in install_deps if dep != 'None']


def matches_any(reference, pattern_list):
    for patt in pattern_list:
        if fnmatch(reference, patt):
            return True
    return False


def recursive_glob(base_directory, regex=None, ignore_list=IGNORE):
    """Uses glob to find all files that match the regex in base_directory.

    @param base_directory: string

    @param regex: string

    @return: set
    """
    if regex is None:
        regex = ''

    files = glob(os.path.join(base_directory, regex))
    for path, dirlist, filelist in os.walk(base_directory):
        for ignored in ignore_list:
            try:
                dirlist.remove(ignored)
            except:
                pass

        for dir_name in dirlist:
            files.extend([fn for fn in glob(os.path.join(path, dir_name, regex))
                          if not matches_any(op.basename(fn), ignore_list)])

    return files


def recursive_remove(work_dir=CWD, regex='*'):
    [os.remove(fn) for fn in recursive_glob(work_dir, regex)]


def recursive_rmtrees(work_dir=CWD, regex='*'):
    [shutil.rmtree(fn, ignore_errors=True) for fn in recursive_glob(work_dir, regex)]


@task
def install_deps():
    # for line in fileinput.input():
    req_filepaths = ['requirements.txt']

    deps = get_requirements(*req_filepaths)

    try:
        for dep_name in deps:
            cmd = "pip install '{0}'".format(dep_name)
            print('#', cmd)
            local(cmd)
    except:
        print('Error installing {}'.format(dep_name))


@task
def version():
    print(__version__)


@task
def install():
    clean()
    install_deps()
    local('python setup.py install')


@task
def develop():
    clean()
    install_deps()
    local('python setup.py develop')


@task
def clean(work_dir=CWD):
    clean_build(work_dir)
    clean_pyc(work_dir)


@task
def clean_build(work_dir=CWD):
    shutil.rmtree('build', ignore_errors=True)
    shutil.rmtree('dist', ignore_errors=True)
    shutil.rmtree('.eggs', ignore_errors=True)
    recursive_rmtrees(work_dir, '__pycache__')
    recursive_rmtrees(work_dir, '*.egg-info')
    recursive_rmtrees(work_dir, '*.egg')
    recursive_rmtrees(work_dir, '.ipynb_checkpoints')


@task
def clean_pyc(work_dir=CWD):
    recursive_remove(work_dir, '*.pyc')
    recursive_remove(work_dir, '*.pyo')
    recursive_remove(work_dir, '*~')


@task
def lint():
    local('flake8 ' + module_name + ' test')


@task
def test():
    local('python setup.py test')


@task
def test_all():
    local('tox')


@task
def coverage():
    local('coverage local --source ' + module_name + ' setup.py test')
    local('coverage report -m')
    local('coverage html')
    local('open htmlcov/index.html')


@task
def docs(doc_type='html'):
    os.remove(op.join('docs', module_name + '.rst'))
    os.remove(op.join('docs', 'modules.rst'))
    local('sphinx-apidoc -o docs/ ' + module_name)
    os.chdir('docs')
    local('make clean')
    local('make ' + doc_type)
    os.chdir(CWD)
    local('open docs/_build/html/index.html')


@task
def release():
    clean()
    local('pip install -U pip setuptools twine wheel')
    local('python setup.py sdist bdist_wheel')
    #local('python setup.py bdist_wheel upload')
    local('twine upload dist/*')


@task
def sdist():
    clean()
    local('python setup.py sdist')
    local('python setup.py bdist_wheel upload')
    print(os.listdir('dist'))


@task
def print_init_file(dirpath=CWD):
    ignore         = ['__init__.py', 'tests', 'install_deps.py', 'fabfile.py']
    files          = recursive_glob(dirpath, regex='*.py', ignore_list=ignore)
    laminy_idx     = files[0].split(op.sep).index('laminy') + 2

    files_no_ext   = [ ''.join(f.split('.')[0:-1])           for f in files]
    relative_names = ['.'.join(f.split(op.sep)[laminy_idx:]) for f in files_no_ext]
    basenames      = ['.'.join(f.split(op.sep)[-1:])         for f in files_no_ext]
    try:
        basenames.remove('__init__')
    except:
        pass

    for name in relative_names:
        print("from .{0} import {1}".format(name, name.split('.')[-1]))

    print("\n")
    print("__all__ = ['{}'".format(basenames[0]))
    for name in basenames[1:-1]:
        print("           '{}',".format(name))
    print("           '{}']".format(basenames[-1]))
