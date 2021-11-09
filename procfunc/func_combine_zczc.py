#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: func_combine_zczc.py

"""
Created on Aug 31, 2021

@author: anduin
"""

import copy
import pandas as pd
import numpy as np

import public
from publictype.fixparamtypes import FixParamTypes
from publictype.columnnames import ColumnNames

func_name = 'combine_zczc'

#读combine_zczc函数需要的参数
def get_params(cfg, section, params, logger):
    #处理过程需要用到的数据集合
    rst = public.get_opt_str(cfg, section, 'data')
    if rst is None or len(rst) == 0:
        raise Exception('combine_zczc %s data error' % section)

    dnrsts = rst.split(',')
    #if len(dnrsts) != 2:
    #    raise Exception('combine_zczc %s %s data format error' % (section, rst))

    params[FixParamTypes.DatasName] = dnrsts
    
    #对应时效没有数据时如何处理
    rst = public.get_opt_float(cfg, section, 'miss_value')
    if rst is None:
        raise Exception('combine_zczc %s miss_value error' % section)
        
    params[FixParamTypes.Miss] = rst

    #对应结果的时效
    rst = public.get_opt_str(cfg, section, 'seq')
    if rst is None:
        raise Exception('combine_zczc %s seq error' % section)
        
    seq = public.parse_list(rst, is_num=True, right_c=True)
    if len(seq) == 0:
        seq = None

    params[FixParamTypes.SeqObj] = seq

#设置运行参数
def set_func_params(save_dt, func_params, src_datas, savecfginfos, dst_datas, logger, stainfos):
    params = {}
    params[FixParamTypes.GridDataList] = {}
    for dn in func_params[FixParamTypes.DatasName]:
        params[FixParamTypes.GridDataList][dn] = src_datas[dn]

    params[FixParamTypes.DstCols] = savecfginfos[FixParamTypes.DstCols]
    params[FixParamTypes.DstGridData] = dst_datas
    params[FixParamTypes.DT] = save_dt

    params[FixParamTypes.SeqObj] = func_params[FixParamTypes.SeqObj]
    params[FixParamTypes.Miss] = func_params[FixParamTypes.Miss]

    params[FixParamTypes.StaInfos] = stainfos

    return params

'''
#不保证与站点表中站点顺序一致
#combine_zczc数据
def run_func(params, logger):
    datas = params[FixParamTypes.GridDataList]
    dt = params[FixParamTypes.DT]
    seq = params[FixParamTypes.SeqObj]
    miss_value = params[FixParamTypes.Miss] if FixParamTypes.Miss in params else 9999.0
    dstcols = params[FixParamTypes.DstCols]
    dst_datas = params[FixParamTypes.DstGridData]

    stainfos = params[FixParamTypes.StaInfos]

    tmpstainfos = copy.deepcopy(stainfos)
    #tmpstainfos.drop(['level', 'time', 'dtime'], axis=1, inplace=True)
    tmpstainfos.drop([ColumnNames.Level.value, ColumnNames.Time.value, ColumnNames.DTime.value], axis=1, inplace=True)

    alldata = None
    for s in seq:
        curdata = copy.deepcopy(tmpstainfos)
        curdata[ColumnNames.Seq.value] = s

        for curcol in dstcols:
            if curcol == ColumnNames.Seq.value:
                continue

            if curcol in datas and s in datas[curcol]:
                curdata = curdata.merge(datas[curcol][s], on=ColumnNames.StaID.value, how='left')
            else:
                curdata[curcol] = miss_value

        if alldata is None:
            alldata = curdata
        else:
            alldata = alldata.append(curdata)

    alldata.sort_values(by=[ColumnNames.StaID.value, ColumnNames.Seq.value], inplace=True)
    alldata.reset_index(drop=True, inplace=True)
    dst_datas[FixParamTypes.GridData] = alldata.fillna(miss_value)
    '''
#与站点表的站点顺序一致
#combine_zczc数据
def run_func(params, logger):
    datas = params[FixParamTypes.GridDataList]
    dt = params[FixParamTypes.DT]
    seq = params[FixParamTypes.SeqObj]
    miss_value = params[FixParamTypes.Miss] if FixParamTypes.Miss in params else 9999.0
    dstcols = params[FixParamTypes.DstCols]
    dst_datas = params[FixParamTypes.DstGridData]

    stainfos = params[FixParamTypes.StaInfos]

    tmpstainfos = copy.deepcopy(stainfos)
    #tmpstainfos.drop(['level', 'time', 'dtime'], axis=1, inplace=True)
    tmpstainfos.drop([ColumnNames.Level.value, ColumnNames.Time.value, ColumnNames.DTime.value], axis=1, inplace=True)

    alldata = pd.DataFrame(np.tile(tmpstainfos.values, len(seq)).reshape((len(seq)*len(tmpstainfos), len(tmpstainfos.columns))), columns=tmpstainfos.columns)
    alldata[ColumnNames.StaID.value] = alldata[ColumnNames.StaID.value].astype(int)
    alldata[ColumnNames.Alt.value] = alldata[ColumnNames.Alt.value].astype(int)
    alldata[ColumnNames.Seq.value] = np.tile(seq, len(tmpstainfos))

    for curcol in dstcols:
        if curcol == ColumnNames.Seq.value:
            continue
        
        coldata = None

        for s in seq:
            curdata = None
            if curcol in datas and s in datas[curcol]:
                curdata = copy.deepcopy(datas[curcol][s])
            else:
                curdata = pd.DataFrame(tmpstainfos[ColumnNames.StaID.value])
                curdata[curcol] = miss_value
                
            curdata[ColumnNames.Seq.value] = s

            if coldata is None:
                coldata = curdata
            else:
                coldata = coldata.append(curdata)

        alldata = alldata.merge(coldata, on=[ColumnNames.StaID.value, ColumnNames.Seq.value], how='left')

    #alldata.reset_index(drop=True, inplace=True)
    dst_datas[FixParamTypes.GridData] = alldata.fillna(miss_value)

if __name__ == '__main__':
    print('done')
