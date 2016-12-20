#!/usr/bin/env python
# -*- coding:utf-8 -*-
#  Author: Jason Wang

from Agent.plugins.linux import sysinfo




def LinuxSysInfo():
    #print __file__
    return  sysinfo.collect()


def WindowsSysInfo():
    from Agent.plugins.windows import sysinfo as win_sysinfo
    return win_sysinfo.collect()


