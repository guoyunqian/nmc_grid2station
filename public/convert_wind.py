#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: convert_wind.py

'''
Created on Sept 21, 2021

@author: anduin
'''

import numpy as np
import math
import copy

#转换uv为ds，输入为numpy数组
def convert_uv_to_ds(u, v, srcdefault=None, dstdefault=None, needcopy=False):
    utmp = u
    vtmp = v
    if needcopy:
        utmp = copy.deepcopy(u)
        vtmp = copy.deepcopy(v)

    if srcdefault is not None and (not np.isnan(srcdefault)):
        utmp[utmp == srcdefault] = np.nan
        vtmp[vtmp == srcdefault] = np.nan

    s = np.sqrt(np.square(utmp) + np.square(vtmp))
    
    tmp = 270.0 - np.arctan2(vtmp, utmp) * 180.0 / np.pi
    d = ((tmp * 100).astype(int) % 36000 / 100.0)

    if dstdefault is not None and (not np.isnan(dstdefault)):
        s[np.isnan(s)] = dstdefault
        d[np.isnan(d)] = dstdefault

    return (d,s)

#转换ds为uv，输入为d和s的meteva格点数据
def convert_ds_to_uv(d, s, srcdefault=None, dstdefault=None, needcopy=False):
    dtmp = d
    stmp = s
    if needcopy:
        dtmp = copy.deepcopy(d)
        stmp = copy.deepcopy(s)

    if srcdefault is not None and (not np.isnan(srcdefault)):
        dtmp[dtmp == srcdefault] = np.nan
        stmp[stmp == srcdefault] = np.nan

    tmp = (270.0 - dtmp) * np.pi / 180.0

    u = stmp * np.cos(tmp)
    v = stmp * np.sin(tmp)
    
    if dstdefault is not None and (not np.isnan(dstdefault)):
        u[np.isnan(u)] = dstdefault
        v[np.isnan(v)] = dstdefault

    return (u,v)

if __name__ == '__main__':
    u = np.array([3, 6])
    v = np.array([4, 8])

    d,s = convert_uv_to_ds(u, v)
    print(d)
    print(s)

    u, v = convert_ds_to_uv(d, s)
    print(u)
    print(v)

    print('test done')


