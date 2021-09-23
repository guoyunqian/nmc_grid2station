#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: readfuncnames.py

'''
Created on Sep 7, 2021

@author: anduin
'''

from enum import Enum
class ReadFuncNames(Enum):
    #读二进制的格点
    read_grid_bin = 'read_grid_bin'
    #读二进制的格点uv风，转成风向风速
    read_grid_bin_wind_from_uv_to_ds = 'read_grid_bin_wind_from_uv_to_ds'

if __name__ == '__main__':
    a = ReadFuncNames.read_grid_bin
    print(a.value)
    print(a.name)
    print(ReadFuncNames.read_grid_bin)
    
    print(ReadFuncNames['read_grid_bin'])
    
    print('test done')