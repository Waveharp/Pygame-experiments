# for py2exe...will not install platakart

from distutils.core import setup
import pymunk
import pygame
import py2exe
import glob
import os.path

pygame_dir = os.path.dirname(pygame.base.__file__)
pymunk_dir = os.path.dirname(pymunk.__file__)

required_libs = (
    "libfreetype-6.dll",
    "libogg-0.dll",
    "sdl_ttf.dll",
)


def find_data_files(source, target, patterns):
    """Locates the specified data-files and returns the matches
    in a data_files compatible format.

    source is the root of the source data tree.
        Use '' or '.' for current directory.
    target is the root of the target data tree.
        Use '' or '.' for the distribution directory.
    patterns is a sequence of glob-patterns for the files you want to copy.
    """
    if glob.has_magic(source) or glob.has_magic(target):
        raise ValueError("Magic not allowed in src, target")
    ret = {}
    for pattern in patterns:
        pattern = os.path.join(source, pattern)
        for filename in glob.glob(pattern):
            if os.path.isfile(filename):
                targetpath = os.path.join(
                    target, os.path.relpath(filename, source))
                path = os.path.dirname(targetpath)
                ret.setdefault(path, []).append(filename)
    return sorted(ret.items())

data_files = find_data_files(
    os.path.join('platakart', 'resources'),
    os.path.join('resources'),
    '*')

data_files.extend(find_data_files(
    os.path.join('config'),
    os.path.join('config'),
    '*'))

data_files.append(os.path.join(pymunk_dir, 'chipmunk.dll'))

origIsSystemDLL = py2exe.build_exe.isSystemDLL
def isSystemDLL(pathname):
    print pathname
    if os.path.basename(pathname).lower() in required_libs:
        return 0
    return origIsSystemDLL(pathname)
py2exe.build_exe.isSystemDLL = isSystemDLL

setup(
    #packages=['platakart'],
    #package_dir = {'platakart': 'platakart'},
    #package_data = {'platakart': ['resources/*']},

    data_files = data_files,

    options = {
            "py2exe": {
                "dll_excludes": ['MSVCP90.dll'],
                'optimize': 2,
                'bundle_files': 1,
                'compressed': 1,
                'packages': ['platakart',
                             'pymunk',
                             'pubsub',
                             'pymunktmx',
                             'pytmx',
                             'pyscroll',
                             'pygame'],
            }
        },
    console = [{'script': 'run_platakart.py'}], requires=['pymunk', 'pubsub',
                                                          'pyscroll',
                                                          'pymunktmx']
)