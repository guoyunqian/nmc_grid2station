#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: get_value.py

'''
Created on Sept 9, 2021

@author: anduin
'''

import numpy as np

#转换一个字符串为数值，支持numpy.nan
def get_value_from_str(s):
    if s is None:
        return None
    if type(s) is not str:
        raise Exception('not support')

    if len(s) == 0:
        return None

    if s == 'nan':
        return np.nan
    elif s.find('.'):
        return float(s)
    else:
        return int(s)

if __name__ == '__main__':

    print('test done')


