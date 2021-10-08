#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: cfg_main.py

'''
Created on Apr 26, 2021

@author: anduin
'''

import os
import datetime

import public
import public.get_value as get_value
from publictype.fixparamtypes import FixParamTypes
from publictype.interptypes import InterpTypes
from publictype.readfuncnames import ReadFuncNames
from publictype.columnnames import ColumnNames
from cfg_srcdata import CfgSrcData
from zczc.zczcpublictype import ZczcPublicType
import procfunc.procfuncs as proc_funcs

class CfgMain(object):
    def __init__(self, logger):
        self.logger = logger

        #配置文件路径
        self.path = None
        #保存数据的信息
        self.savecfginfos = None
        #站点信息
        self.stainfos = None
        #数据源列表
        self.srccfglist = None
        #处理过程列表
        self.proccfglist = None

    #保存结果的信息
    def parse_save_config(self, cfg):
        self.savecfginfos = {}

        section = 'save_config'

        #path
        rst = public.get_opt_str(cfg, section, 'path')
        if rst is None:
            raise Exception('save_config path error')

        self.savecfginfos[FixParamTypes.DDict] = rst

        #fn_fmt
        rst = public.get_opt_str(cfg, section, 'fn_fmt')
        if rst is None:
            raise Exception('save_config fn_fmt error')

        self.savecfginfos[FixParamTypes.DFnFmt] = rst
        
        #fhs
        rst = public.get_opt_str(cfg, section, 'fhs')
        if rst is None:
            raise Exception('save_config fhs error')
        
        fhs = public.parse_list(rst, is_num=True, right_c=True)
        if len(fhs) == 0:
            fhs = None

        self.savecfginfos[FixParamTypes.DFHS] = fhs
        
        #提前多久生成起报时的数据
        rst = public.get_opt_int(cfg, section, 'fhs_delta')
        if rst is None:
            raise Exception('save_config fhs_delta error')
        
        self.savecfginfos[FixParamTypes.DFhsDelta] = rst

        #product_desc
        rst = public.get_opt_str(cfg, section, 'product_desc')
        if rst is None:
            raise Exception('save_config product_desc error')

        self.savecfginfos[FixParamTypes.ProductDesc] = rst
        
        #product_code
        rst = public.get_opt_str(cfg, section, 'product_code')
        if rst is None:
            raise Exception('save_config product_code error')

        self.savecfginfos[FixParamTypes.ProductCode] = rst
        
        #columns zczc文件的列名，包括时效
        rst = public.get_opt_str(cfg, section, 'columns')
        if rst is None or len(rst) == 0:
            raise Exception('save_config columns error')

        if rst == 'default':
            rst = ZczcPublicType.columns
        else:
            srsts = rst.split(',')
            rst = []
            for srst in srsts:
                rst.append(ColumnNames[srst])

        self.savecfginfos[FixParamTypes.DstCols] = rst
        
        #CCCC
        rst = public.get_opt_str(cfg, section, 'CCCC')
        if rst is None:
            raise Exception('save_config CCCC error')

        self.savecfginfos[FixParamTypes.CCCC] = rst
        
        '''
        #default
        rst = public.get_opt_str(cfg, section, 'default')
        #if rst is None or len(rst) == 0:
        #    raise Exception('save_config default error')

        self.savecfginfos[FixParamTypes.Default] = get_value.get_value_from_str(rst)
        '''

        #数据精度
        rst = public.get_opt_int(cfg, section, 'decimals')
        if rst is None:
            #raise Exception('save_config decimals error')
            self.savecfginfos[FixParamTypes.Decimals] = 1
        else:
            self.savecfginfos[FixParamTypes.Decimals] = rst

        #经纬度精度
        rst = public.get_opt_int(cfg, section, 'scale_decimals')
        if rst is None:
            #raise Exception('save_config scale_decimals error')
            self.savecfginfos[FixParamTypes.ScaleDecimals] = 3
        else:
            self.savecfginfos[FixParamTypes.ScaleDecimals] = rst
            
        #是否保存hdf格式
        rst = public.get_opt_int(cfg, section, 'save_hdf')
        if rst is None:
            #raise Exception('save_config save_hdf error')
            self.savecfginfos[FixParamTypes.SaveHDF] = 0
        else:
            self.savecfginfos[FixParamTypes.SaveHDF] = rst
        
        #hdf文件保存路径
        rst = public.get_opt_str(cfg, section, 'path_hdf')
        if rst is None and self.savecfginfos[FixParamTypes.SaveHDF] != 0:
            raise Exception('save_config path_hdf error')
        else:
            self.savecfginfos[FixParamTypes.DDictHDF] = rst
        
        #hdf文件文件名格式
        rst = public.get_opt_str(cfg, section, 'fn_fmt_hdf')
        if rst is None and self.savecfginfos[FixParamTypes.SaveHDF] != 0:
            raise Exception('save_config fn_fmt_hdf error')
        else:
            self.savecfginfos[FixParamTypes.DFnFmtHDF] = rst
        
    #站点信息
    def parse_sta_infos_config(self, cfg):
        self.stainfos = {}

        section = 'sta_infos'

        #filepath
        rst = public.get_opt_str(cfg, section, 'filepath')
        if rst is None:
            raise Exception('sta_infos filepath error')

        self.stainfos[FixParamTypes.StaPath] = rst

    #解析源数据的信息
    def parse_data_config(self, cfg, basedir, logger=None):
        if logger is None:
            logger = self.logger
            
        self.srccfglist = []

        section_fmt = 'data%02d'

        index = 1
        while(True):
            section = section_fmt % index
            index += 1

            if not cfg.has_section(section):
                break

            srccfg = {}

            srccfg[FixParamTypes.DatasName] = section
            
            #数据源的数据名
            rst = public.get_opt_str(cfg, section, 'name')
            if rst is None or len(rst) == 0:
                raise Exception('%s name error' % section)

            srsts = rst.split(',')
            if len(srsts) == 1:
                srccfg[FixParamTypes.DName] = rst
            else:
                srccfg[FixParamTypes.DName] = srsts

            #数据源配置文件
            rst = public.get_opt_str(cfg, section, 'data')
            if rst is None:
                raise Exception('%s data error' % section)

            if os.path.isabs(rst):
                srccfg[FixParamTypes.CfgFilePath] = rst
            else:
                srccfg[FixParamTypes.CfgFilePath] = os.path.join(basedir, rst)

            cfgobj = CfgSrcData(logger)
            cfgobj.parse(srccfg[FixParamTypes.CfgFilePath])
            srccfg[FixParamTypes.CfgObj] = cfgobj

            #对应结果的时效
            rst = public.get_opt_str(cfg, section, 'seq')
            if rst is None:
                raise Exception('%s seq error' % section)
        
            seq = public.parse_list(rst, is_num=True, right_c=True)
            if len(seq) == 0:
                seq = None

            srccfg[FixParamTypes.DSeq] = seq
            
            #数据源的插值算法
            rst = public.get_opt_str(cfg, section, 'interp')
            if rst is None:
                raise Exception('%s interp error' % section)

            srccfg[FixParamTypes.InterpType] = InterpTypes[rst]
            
            #读的方法
            rst = public.get_opt_str(cfg, section, 'read_func')
            if rst is None:
                raise Exception('%s read_func error' % section)

            srccfg[FixParamTypes.FuncName] = ReadFuncNames[rst]

            self.srccfglist.append(srccfg)
            
    #解析数据处理方法的配置信息
    def parse_proc_config(self, cfg, logger=None):
        self.proccfglist = []

        section_fmt = 'proc%02d'

        index = 1
        while(True):
            section = section_fmt % index
            index += 1

            if not cfg.has_section(section):
                break

            proccfg = {}

            #处理方法
            rst = public.get_opt_str(cfg, section, 'func')
            if rst is None:
                raise Exception('%s func error' % section)
            
            proccfg[FixParamTypes.FuncName] = rst

            proc_funcs.get_func_params(rst, cfg, section, proccfg, logger if logger else self.logger)

            self.proccfglist.append(proccfg)

    #解析主配置文件
    def parse(self, inipath=None, logger=None):
        try:
            if logger is None:
                logger = self.logger

            logger.info('config ini parse start')

            if inipath is None:
                inipath = self.path
            else:
                self.path = inipath

            if inipath is None:
                print('config ini path is none')
                logger.error('config ini path error')
                return False

            cfgobj = public.parse_ini_file(inipath, logger)
            if cfgobj is None:
                print('config ini params error')
                logger.error('config ini params error')
                return False

            self.parse_save_config(cfgobj)

            self.parse_sta_infos_config(cfgobj)

            cfgbasedir = os.path.dirname(inipath)
            self.parse_data_config(cfgobj, cfgbasedir, logger)

            self.parse_proc_config(cfgobj, logger)

            logger.info('config ini parse over')

            return True
        except Exception as data:
            logger.error('config ini parse except %s' % (str(data)))
            return False
            
if __name__ == '__main__':
    cfg = CfgMain()
    
    print('done')
