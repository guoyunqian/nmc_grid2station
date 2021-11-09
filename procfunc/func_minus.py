#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: func_minus.py

"""
Created on May 13, 2021

@author: anduin
"""

import public
from publictype.fixparamtypes import FixParamTypes
from publictype.columnnames import ColumnNames

func_name = 'minus'

#读minus函数需要的参数
def get_params(cfg, section, params, logger):
    #处理过程需要用到的数据集合
    rst = public.get_opt_str(cfg, section, 'data')
    if rst is None or len(rst) == 0:
        raise Exception('select %s data error' % section)

    params[FixParamTypes.DatasName] = rst

    #需要减的数
    rst = public.get_opt_float(cfg, section, 'offset')
    if rst is None:
        raise Exception('select %s offset error' % section)
        
    params[FixParamTypes.Offset] = rst
    
#设置运行参数
def set_func_params(save_dt, func_params, src_datas, savecfginfos, dst_datas, logger):
    params = {}
    params[FixParamTypes.GridDataList] = src_datas[func_params[FixParamTypes.DatasName]]
    params[FixParamTypes.Columns] = func_params[FixParamTypes.DatasName]
    params[FixParamTypes.Offset] = func_params[FixParamTypes.Offset]

    return params

#minus数据
def run_func(params, logger):
    datas = params[FixParamTypes.GridDataList]
    dname = params[FixParamTypes.Columns]
    offset = params[FixParamTypes.Offset]

    for seq in datas.keys():
        datas[seq][dname] -= offset

if __name__ == '__main__':
    print('done')
