#!/usr/bin/env python3

from cx_Freeze import setup, Executable
import os.path
import platform


if platform.system() == 'Windows':
    PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))
    os.environ['TCL_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tcl8.6')
    os.environ['TK_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tk8.6')
    setupOptions = {"build_exe": {"packages": ["pygame", "numpy", "pymunk", "yaml"],
                             "include_files": [
                                 os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tk86t.dll'),
                                 os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tcl86t.dll'),
                                 "chipmunk.dll", "RobotPrograms", "config.yml", "LICENSE", "README.md", "StartSimulation.bat", "codeblocks"]}}
else:
    setupOptions = {"build_exe": {"packages": ["pygame", "numpy", "pymunk", "yaml"],
                    		"include_files": ["libchipmunk.so", "RobotPrograms", "config.yml", "LICENSE", "README.md"],
				"optimize": 2,}}


setup(
    name="Robocup Simulator",
    options=setupOptions,
    executables = [Executable("robotsimul.py")]
    )