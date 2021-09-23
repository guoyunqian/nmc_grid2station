#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: interptypes.py

'''
Created on Aug 26, 2021

@author: anduin
'''

from enum import Enum

class InterpTypes(Enum):
    #格点—>站点 临近点插值
    interp_gs_nearest = 1
    #格点—>站点 双线性插值
    interp_gs_linear = 2
    #格点—>站点 双三次插值
    interp_gs_cubic = 3
    #格点—>格点 双线性插值
    interp_gg_linear = 'MDT_QPE_1hr_N'

    #站点—>格点 反距离权重插值
    interp_sg_idw = 4
    #站点—>格点 cressman插值
    interp_sg_cressman = 5
    #站点—>站点 反距离权重插值
    interp_ss_idw = 6

if __name__ == '__main__':
    a=InterpTypes.interp_gs_nearest
    print(a.value)
    print(InterpTypes.interp_gs_nearest)
    
    print(InterpTypes['interp_gs_nearest'])

    print('test done')