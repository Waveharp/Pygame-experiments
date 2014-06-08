# Compila todo en 1 archivo

from distutils.core import setup
import py2exe
import sys
import os

origIsSystemDLL = py2exe.build_exe.isSystemDLL
def isSystemDLL(pathname):
       if os.path.basename(pathname).lower() in ["sdl_ttf.dll"]:
               return 0
       return origIsSystemDLL(pathname)
py2exe.build_exe.isSystemDLL = isSystemDLL

sys.argv.append("py2exe")

setup(
    console=['hex.py'],    
    options = {'py2exe': {
                        'bundle_files': 1,
                        'excludes': ["Tkconstants", "Tkinter", "tcl", "numpy", "_ssl",
                                       "doctest", "pdb", "unittest", "difflib", "inspect"],
                        'ascii': True
                        }
            }
)