#!/usr/bin/env python3

import sys
from cx_Freeze import setup, Executable


setup(
    name="Robocup Simulator",
    options={"build_exe": {"packages":["pygame","numpy","pymunk"]}},
    executables = [Executable("robotsimul.py")]
    )