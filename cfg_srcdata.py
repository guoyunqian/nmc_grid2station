#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: cfg_srcdata.py

'''
Created on Apr 26, 2021

@author: anduin
'''

import os
import datetime

import public
import public.get_value as get_value
from publictype.fixparamtypes import FixParamTypes as FixParamTypes

class CfgSrcData(object):
    def __init__(self, logger):
        self.logger = logger

        #配置文件路径
        self.path = None
        #数据源的信息
        self.srcinfos = None
        
    def parse_src_config(self, cfg):
        self.srcinfos = {}

        section = 'config'
        #path
        rst = public.get_opt_str(cfg, section, 'path')
        if rst is None:
            raise Exception('config path error')

        self.srcinfos[FixParamTypes.SDict] = rst

        #fn_fmt
        rst = public.get_opt_str(cfg, section, 'fn_fmt')
        if rst is None:
            raise Exception('config fn_fmt error')

        self.srcinfos[FixParamTypes.SFnFmt] = rst
        
        #miss_value
        rst = public.get_opt_str(cfg, section, 'miss_value')
        #if rst is None or len(rst) == 0:
        #    raise Exception('save_config miss_value error')

        self.srcinfos[FixParamTypes.Miss] = get_value.get_value_from_str(rst)
        
        #经度格点数
        rst = public.get_opt_int(cfg, section, 'nlon')
        if rst is None:
            raise Exception('config nlon error')
        
        self.srcinfos[FixParamTypes.NLon] = rst

        #纬度格点数
        rst = public.get_opt_int(cfg, section, 'nlat')
        if rst is None:
            raise Exception('config nlat error')
        
        self.srcinfos[FixParamTypes.NLat] = rst

        #开始经度
        rst = public.get_opt_float(cfg, section, 'slon')
        if rst is None:
            raise Exception('config slon error')
        
        self.srcinfos[FixParamTypes.SLon] = rst

        #开始纬度
        rst = public.get_opt_float(cfg, section, 'slat')
        if rst is None:
            raise Exception('config slat error')
        
        self.srcinfos[FixParamTypes.SLat] = rst

        #结束经度
        rst = public.get_opt_float(cfg, section, 'elon')
        if rst is None:
            raise Exception('config elon error')
        
        self.srcinfos[FixParamTypes.ELon] = rst

        #结束纬度
        rst = public.get_opt_float(cfg, section, 'elat')
        if rst is None:
            raise Exception('config elat error')
        
        self.srcinfos[FixParamTypes.ELat] = rst

        #经度分辨率
        rst = public.get_opt_float(cfg, section, 'dlon')
        if rst is None:
            raise Exception('config dlon error')
        
        self.srcinfos[FixParamTypes.DLon] = rst

        #纬度分辨率
        rst = public.get_opt_float(cfg, section, 'dlat')
        if rst is None:
            raise Exception('config dlat error')
        
        self.srcinfos[FixParamTypes.DLat] = rst


    def parse(self, inipath=None, logger=None):
        try:
            if logger is None:
                logger = self.logger

            if inipath is None:
                inipath = self.path
            else:
                self.path = inipath

            if inipath is None:
                print('CfgSrcData ini path is none')
                logger.error('CfgSrcData ini path is none')
                return None

            cfgobj = public.parse_ini_file(inipath)
            if cfgobj is None:
                print('CfgSrcData ini params error')
                logger.error('CfgSrcData ini params error')
                return None

            self.parse_src_config(cfgobj)

            return True
        except Exception as data:
            logger.error('CfgSrcData parse except %s' % (str(data)))
            return False
            
if __name__ == '__main__':
    print('done')
