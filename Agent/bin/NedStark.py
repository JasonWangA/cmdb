#!/usr/bin/env python
# -*- coding:utf-8 -*-
#  Author: Jason Wang
import os,sys,platform

#for linux
if platform.system() == "Windows":
    BASE_DIR = '\\'.join(os.path.abspath(os.path.dirname(__file__)).split('\\')[:-1])
    print(BASE_DIR)
else:
    BASE_DIR = '/'.join(os.path.abspath(os.path.dirname(__file__)).split('/')[:-1])
sys.path.append(BASE_DIR)

from Agent.core import HouseStark #main


if __name__ == '__main__':

    HouseStark.ArgvHandler(sys.argv)