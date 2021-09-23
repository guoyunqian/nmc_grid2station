#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: zczcpublictype.py

'''
Created on Apr 6, 2021

@author: anduin
'''
import datetime

from logmodule.loglib import *
from publictype.columnnames import ColumnNames as cn

class ZczcPublicType:
    default_value = 999.9
    fileid = 'ZCZC'
    TTAAii = 'FSCI50'
    fcst_time_fmt = '%Y%m%d%H'
    endstr = 'NNNN'

    #时效#温度#相对湿度#风向#风速
    #气压#降水量#总云量#低云量#天气现象
    #能见度#最高温度#最低温度#最大相对湿度# 最小相对湿度
    #24小时降水量#12小时降水量#12小时总云量#12小时低云量#12小时天气现象
    #12小时风向#12小时风速
    columns = [cn.Seq.value, cn.Tem.value, cn.RH.value, cn.Wind_D.value, cn.Wind_S.value,
                    cn.AP.value, cn.Pre.value, cn.TC.value, cn.LC.value, cn.WP.value,
                    cn.VIS.value, cn.TMX.value, cn.TMI.value, cn.RHMX.value, cn.RHMI.value,
                    cn.TP24H.value, cn.TP12H.value, cn.TC12H.value, cn.LC12H.value, cn.WP12H.value,
                    cn.Wind_D_12H.value, cn.Wind_S_12H.value
                    ]

    columns_all = [cn.StaID.value, cn.Lon.value, cn.Lat.value, cn.Alt.value].extend(columns)


if __name__ == '__main__':
    print(ZczcPublicType.default_value)

    print(ZczcPublicType.columns)

    print(ZczcPublicType.columns_all)

    print('test done')


