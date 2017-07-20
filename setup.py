#!/usr/bin/env python3

import sys
from cx_Freeze import setup, Executable
import os.path
import platform

if platform.system() == 'Windows':
    PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))
    os.environ['TCL_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tcl8.6')
    os.environ['TK_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tk8.6')
    setupOptions = {"build_exe": {"packages": ["pygame", "numpy", "pymunk"],
                             "include_files": [
                                 os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tk86t.dll'),
                                 os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tcl86t.dll'),
                                 "chipmunk.dll", "Team1", "Team2"]}}
else:
    setupOptions = {"build_exe": {"packages": ["pygame", "numpy", "pymunk"],
                    "include_files": ["libchipmunk.so", "Team1", "Team2"]}}


setup(
    name="Robocup Simulator",
    options=setupOptions,
    executables = [Executable("robotsimul.py")]
    )