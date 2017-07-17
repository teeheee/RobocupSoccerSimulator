#!/usr/bin/env python

#TODO check out https://pythonprogramming.net/converting-pygame-executable-cx_freeze/ could be better

from distutils.core import setup

setup(name='RobocupSimulator',
      version='1.0',
      description='Nothing interesting...',
      author='Alexander Ulbrich',
      author_email='alexander.ulbrich@uni-ulm.de',
      url='https://github.com/teeheee/RobocupSoccerSimulator',
      install_requires=['numpy','pymunk','pygame']
     )